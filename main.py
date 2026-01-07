# main.py - TO'G'RI VERSIYA
import sys
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

print("=== BOTNI SOZLASH ===")

# =========== TOKEN OLISH (XAVFSIZ) ===========
def get_token():
    """
    Tokenni faqat environment variable yoki .env faylidan olish
    KODDA HECH QANDAY TOKEN YO'Q!
    """
    
    # 1. Environment variable dan
    token = os.environ.get("BOT_TOKEN")
    if token:
        print("✅ Token environment variable dan olindi")
        return token
    
    # 2. .env faylidan
    try:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.environ.get("BOT_TOKEN")
        if token:
            print("✅ Token .env faylidan olindi")
            return token
    except ImportError:
        pass
    
    # 3. TOKEN TOPILMADI - FAKAT SERVERDA ISHLASHI KERAK
    print("❌ XATO: BOT_TOKEN topilmadi!")
    print("=======================================")
    print("QO'LLANMA:")
    print("1. Render.com da: Environment Variables > BOT_TOKEN")
    print("2. Localda: .env fayl yarating yoki BOT_TOKEN o'zgaruvchisi")
    print("3. Token: BotFather dan /token buyrug'i bilan oling")
    print("=======================================")
    sys.exit(1)

# Tokenni xavfsiz olish
TOKEN = get_token()
print(f"🔐 Token muvaffaqiyatli yuklandi")

# =========== QOLGAN KOD ===========

# 1. TO'G'RI PAPKA YO'LINI BELGILASH
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"📂 Joriy papka: {os.getcwd()}")

# 2. uz_trans.py ni yuklash
try:
    with open('uz_trans.py', 'r', encoding='utf-8') as f:
        exec(f.read(), globals())
    print("✅ uz_trans.py yuklandi!")
    
    # Test
    if 'to_cyrillic' in globals():
        test_result = to_cyrillic("Salom")
        print(f"✅ Test muvaffaqiyatli: 'Salom' -> '{test_result}'")
    else:
        sys.path.insert(0, script_dir)
        import uz_trans
        globals()['to_cyrillic'] = uz_trans.to_cyrillic
        globals()['to_latin'] = uz_trans.to_latin
        print("✅ Modul sifatida import qilindi!")
        
except Exception as e:
    print(f"❌ uz_trans.py yuklashda xato: {e}")
    exit(1)

# 3. Botni yaratish
ADMIN_ID = 1051632082
bot = telebot.TeleBot(TOKEN)

# 4. Web App URL
WEB_APP_URL = "https://telegram-bot-krill-lotin-krill-translater.onrender.com"

# =========== BOT HANDLERS ===========

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Inline keyboard yaratish
    markup = InlineKeyboardMarkup()
    
    # Web App tugmasi
    web_app_btn = InlineKeyboardButton(
        text="🌐 Web App'ni ochish", 
        web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)
    )
    
    # Yordam tugmasi
    help_btn = InlineKeyboardButton(
        text="❓ Qanday ishlatish", 
        callback_data="help_info"
    )
    
    markup.add(web_app_btn)
    markup.add(help_btn)
    
    welcome = f"""
👋 *Assalomu alaykum, {message.from_user.first_name}!*

🤖 *Kirill-Lotin AI Translater* botiga xush kelibsiz!

✨ *YANGI!* Endi sizda **Web App** mavjud:

🌐 *Web App afzalliklari:*
• Chiroyli interfeys
• Tezkor konvertatsiya  
• Natijani nusxalash
• Tugmalar orqali oson ishlash
• Kompyuter va telefon uchun

📱 *Oddiy ishlash:* Faqat matn yuboring
🌐 *Web App:* Tugma bosish kifoya!

*Barchasi bir joyda!* 🚀
"""
    
    bot.send_message(
        message.chat.id,
        welcome,
        parse_mode='Markdown',
        reply_markup=markup
    )

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "help_info":
        help_text = """
🆘 *Qanday ishlatish?*

*Bot orqali:*
1. Faqat matn yuboring
2. Bot avtomatik aniqlab konvertatsiya qiladi

*Web App orqali:*
1. "🌐 Web App'ni ochish" tugmasini bosing
2. Matnni kiritish maydoniga yozing
3. "Lotin → Kirill" yoki "Kirill → Lotin" tugmasini bosing
4. Natijani nusxalash tugmasi bilan nusxalang

*Qaysi biri yaxshi?*
📱 *Bot:* Tezkor, oddiy matnlar uchun
🌐 *Web App:* Ko'proq funksiyalar, chiroyli interfeys
"""
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['test'])
def test_bot(message):
    """Bot funksiyalarini test qilish"""
    try:
        test_text = "Salom O'zbekiston"
        kirill = to_cyrillic(test_text)
        latin = to_latin(kirill)
        
        result = f"""
✅ *Bot ishlayapti!*

Test matn: `{test_text}`
Kirill: `{kirill}`
Qayta lotin: `{latin}`
"""
        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Testda xato: {str(e)}")

# Web App uchun alohida handler
@bot.message_handler(commands=['webapp'])
def send_webapp_link(message):
    markup = InlineKeyboardMarkup()
    
    web_app_btn = InlineKeyboardButton(
        text="🌐 Web App'ni ochish", 
        web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)
    )
    
    open_in_browser = InlineKeyboardButton(
        text="🔗 Brauzerda ochish",
        url=WEB_APP_URL
    )
    
    markup.add(web_app_btn)
    markup.add(open_in_browser)
    
    bot.send_message(
        message.chat.id,
        f"🌐 *Web App manzili:*\n\n`{WEB_APP_URL}`\n\nTugma orqali ochishingiz mumkin:",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def convert_text(message):
    """Asosiy konvertatsiya funksiyasi"""
    text = message.text
    
    # Buyruqlarni chetlab o'tish
    if text.startswith('/'):
        return
    
    try:
        # Matn kirill yoki lotin ekanligini aniqlash
        if any('\u0400' <= char <= '\u04FF' for char in text):
            # Kirill -> Lotin
            converted = to_latin(text)
            response_text = f"🔤 *Lotin alifbosida:*\n\n`{converted}`"
        else:
            # Lotin -> Kirill
            converted = to_cyrillic(text)
            response_text = f"🔤 *Kirill alifbosida:*\n\n`{converted}`"
        
        bot.reply_to(message, response_text, parse_mode='Markdown')
        
    except Exception as e:
        error_text = f"❌ *Xatolik yuz berdi:*\n\n`{str(e)}`"
        bot.reply_to(message, error_text, parse_mode='Markdown')

# 5. Botni ishga tushirish
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 BOT ISHGA TUSHMOQDA...")
    print("="*50)
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Botda xato: {e}")