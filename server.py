from flask import Flask, send_from_directory, jsonify, request
import os
import threading
import time
import requests

# Load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')
LIBRETRANSLATE_URL = os.environ.get(
    'LIBRETRANSLATE_URL', 'http://127.0.0.1:5000'
).rstrip('/')

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def home():
    # Health/ping endpoint for external cron pings (returns 200)
    webapp_path = os.path.join(APP_ROOT, 'webapp.html')
    if os.path.exists(webapp_path):
        return send_from_directory(APP_ROOT, 'webapp.html')
    return jsonify({'status': 'ok'})


@app.route('/webapp')
def webapp():
    return home()


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'kirill-lotin-bot'})


@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.get_json(silent=True) or {}
    text = str(data.get('text', '')).strip()
    target = str(data.get('target', '')).strip()

    if not text or not target:
        return jsonify({'error': 'text va target majburiy'}), 400

    try:
        response = requests.post(
            f'{LIBRETRANSLATE_URL}/translate',
            json={
                'q': text,
                'source': 'auto',
                'target': target,
                'format': 'text',
            },
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        translated_text = result.get('translatedText')
        if not translated_text:
            return jsonify({'error': 'LibreTranslate bo\'sh javob qaytardi'}), 502
        return jsonify({'translatedText': translated_text})
    except requests.RequestException as error:
        return jsonify({
            'error': 'LibreTranslate xizmatiga ulanib bo\'lmadi',
            'details': str(error),
        }), 502


def run_flask():
    port = int(os.environ.get('PORT', 8080))
    # On Render (Linux), bind to 0.0.0.0
    app.run(host='0.0.0.0', port=port)


def start_bot_in_thread():
    """If main.py exposes start_bot(), run it in a daemon thread."""
    try:
        import main as bot_module

        if hasattr(bot_module, 'start_bot'):
            t = threading.Thread(target=bot_module.start_bot, daemon=True)
            t.start()
        else:
            # Fallback: if main.py runs polling on import, import in thread
            def _import_and_run():
                try:
                    import importlib
                    importlib.reload(bot_module)
                except Exception:
                    pass

            t = threading.Thread(target=_import_and_run, daemon=True)
            t.start()
    except Exception:
        pass


if __name__ == '__main__':
    # Start the bot in a background thread so Flask can serve HTTP
    start_bot_in_thread()

    # Run Flask (main thread)
    run_flask()