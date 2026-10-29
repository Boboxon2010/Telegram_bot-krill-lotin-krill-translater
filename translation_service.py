import os
import threading
from typing import Callable
from urllib.parse import quote

import requests


class TranslationServiceError(RuntimeError):
    """Raised when every configured translation provider fails."""


class TranslationService:
    def __init__(self) -> None:
        self.timeout = float(os.environ.get("TRANSLATION_TIMEOUT", "30"))
        self.min_interval = float(os.environ.get("TRANSLATION_MIN_INTERVAL", "1.2"))
        self._lock = threading.Lock()
        self._last_request = 0.0
        self.providers: dict[str, Callable[[str, str], str]] = {
            "lingva": self._translate_lingva,
            "mymemory": self._translate_mymemory,
            "simply": self._translate_simply,
            "libre": self._translate_libre_remote,
        }
        configured_order = os.environ.get(
            "TRANSLATION_PROVIDER_ORDER",
            "lingva,mymemory,simply,libre",
        )
        self.provider_order = [
            name.strip().lower()
            for name in configured_order.split(",")
            if name.strip().lower() in self.providers
        ] or ["libre"]

    def translate(self, text: str, target: str) -> str:
        if not text.strip():
            raise TranslationServiceError("Tarjima uchun matn bo'sh")
        if not target.strip():
            raise TranslationServiceError("Tarjima tili ko'rsatilmagan")

        errors = []
        for provider_name in self.provider_order:
            try:
                result = self.providers[provider_name](text, target)
                if result and result.strip():
                    return result.strip()
                errors.append(f"{provider_name}: bo'sh javob")
            except Exception as error:
                errors.append(f"{provider_name}: {error}")

        raise TranslationServiceError(
            "Barcha tarjima xizmatlari vaqtincha ishlamayapti: "
            + "; ".join(errors)
        )

    def _request_slot(self) -> None:
        with self._lock:
            import time

            wait_time = self.min_interval - (time.monotonic() - self._last_request)
            if wait_time > 0:
                time.sleep(wait_time)
            self._last_request = time.monotonic()

    def _translate_mymemory(self, text: str, target: str) -> str:
        params = {
            "q": text,
            "langpair": f"autodetect|{target}",
        }
        email = os.environ.get("MYMEMORY_EMAIL")
        if email:
            params["de"] = email
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        if str(data.get("responseStatus")) != "200":
            raise RuntimeError(data.get("responseDetails", "MyMemory xatosi"))
        return data.get("responseData", {}).get("translatedText", "")

    def _translate_simply(self, text: str, target: str) -> str:
        base_url = os.environ.get(
            "SIMPLYTRANSLATE_API_URL",
            "https://simplytranslate.org/api/translate",
        ).rstrip("/")
        response = requests.get(
            base_url,
            params={
                "engine": os.environ.get("SIMPLYTRANSLATE_ENGINE", "google"),
                "from": "auto",
                "to": target,
                "text": text,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self._translation_from_response(response)

    def _translate_lingva(self, text: str, target: str) -> str:
        base_url = os.environ.get("LINGVA_API_URL", "https://lingva.ml/api/v1").rstrip("/")
        source = os.environ.get("LINGVA_SOURCE_LANGUAGE", "auto")
        response = requests.get(
            f"{base_url}/{quote(source)}/{quote(target)}/{quote(text)}",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("translation", "")

    def _translate_libre_remote(self, text: str, target: str) -> str:
        urls = os.environ.get("LIBRETRANSLATE_REMOTE_URLS", "").split(",")
        if not any(url.strip() for url in urls):
            raise RuntimeError("remote LibreTranslate URL sozlanmagan")
        last_error = None
        for url in urls:
            base_url = url.strip().rstrip("/")
            if not base_url:
                continue
            try:
                response = requests.post(
                    f"{base_url}/translate",
                    json={
                        "q": text,
                        "source": "auto",
                        "target": target,
                        "format": "text",
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                translated = response.json().get("translatedText", "")
                if translated:
                    return translated
            except Exception as error:
                last_error = error
        raise last_error or RuntimeError("remote LibreTranslate javob bermadi")

    @staticmethod
    def _translation_from_response(response: requests.Response) -> str:
        try:
            data = response.json()
        except ValueError:
            return response.text
        if isinstance(data, dict):
            return TranslationService._translation_from_json(data)
        raise RuntimeError("provider javobi noto'g'ri formatda")

    @staticmethod
    def _translation_from_json(data: dict) -> str:
        for key in ("translation", "translatedText", "translated_text", "text", "result"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
        raise RuntimeError("provider javobida tarjima topilmadi")
