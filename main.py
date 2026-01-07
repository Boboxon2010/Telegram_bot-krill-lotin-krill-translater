# main.py - GITHUB VERSIYASI (TOKEN XAVFSIZ)
import sys
import os
import telebot

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

# =========== QOLGAN KOD (O'ZGARMASIN) ===========

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

# 3. Botni ishga tushirish
ADMIN_ID = 1051632082

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome = """
👋 *Assalomu alaykum! Kirill-Lotin botiga xush kelibsiz!*

📝 *Menga matn yuboring:*
• Lotin alifbosida bo'lsa → Kirill alifbosiga
• Kirill alifbosida bo'lsa → Lotin alifbosiga o'giraman.

*Namunalar:*
"Salom" → "Салом"
"Ўзбекистон" → "O'zbekiston"

🌐 *Web App:* Serverda mavjud
"""
    bot.reply_to(message, welcome, parse_mode='Markdown')

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

# 4. Botni ishga tushirish
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 BOT ISHGA TUSHMOQDA...")
    print("="*50)
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Botda xato: {e}")