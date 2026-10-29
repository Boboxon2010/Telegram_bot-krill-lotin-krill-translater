from flask import Flask, send_from_directory, jsonify, request
import os
import threading
from telebot import types
from translation_service import TranslationService, TranslationServiceError

# Load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')
translation_service = TranslationService()
bot_module = None

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


@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    if bot_module is None or bot_module.bot is None:
        return jsonify({'error': 'bot hali ishga tushmagan'}), 503

    secret = os.environ.get('TELEGRAM_WEBHOOK_SECRET')
    if secret and request.headers.get('X-Telegram-Bot-Api-Secret-Token') != secret:
        return jsonify({'error': 'ruxsat berilmagan'}), 403

    update = types.Update.de_json(request.get_data(as_text=True))
    bot_module.bot.process_new_updates([update])
    return jsonify({'ok': True})


@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.get_json(silent=True) or {}
    text = str(data.get('text', '')).strip()
    target = str(data.get('target', '')).strip()

    if not text or not target:
        return jsonify({'error': 'text va target majburiy'}), 400

    try:
        return jsonify({
            'translatedText': translation_service.translate(text, target),
        })
    except TranslationServiceError:
        return jsonify({
            'error': 'Barcha tarjima xizmatlari vaqtincha ishlamayapti',
        }), 503
    except Exception as error:
        return jsonify({
            'error': 'Tarjima xizmatida ichki xato',
            'details': str(error),
        }), 502


def run_flask():
    port = int(os.environ.get('PORT', 8080))
    # On Render (Linux), bind to 0.0.0.0
    app.run(host='0.0.0.0', port=port)


def start_bot_in_thread():
    """If main.py exposes start_bot(), run it in a daemon thread."""
    global bot_module
    try:
        import main as bot_module
        globals()['bot_module'] = bot_module

        webhook_base = os.environ.get(
            'WEBHOOK_URL', os.environ.get(
                'WEB_APP_URL', getattr(bot_module, 'WEB_APP_URL', '')
            )
        ).rstrip('/')
        webhook_secret = os.environ.get('TELEGRAM_WEBHOOK_SECRET')
        if webhook_base and bot_module.bot is not None:
            webhook_url = f'{webhook_base}/telegram/webhook'
            bot_module.bot.remove_webhook()
            if webhook_secret:
                bot_module.bot.set_webhook(
                    url=webhook_url,
                    secret_token=webhook_secret,
                )
            else:
                bot_module.bot.set_webhook(url=webhook_url)
            print(f'✅ Telegram webhook o\'rnatildi: {webhook_url}')
            return

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