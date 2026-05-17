# main.py - FAQAT REKLAMA VA ADMIN TUZATILGAN
import sys
import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import tempfile
import uuid

print("=== KIRILL-LOTIN AI TRANSLATER BOT ===")

# =========== SOZLAMALAR ===========
ADMIN_IDS = [1051632082]  # SIZNING ID'INGIZ
WEB_APP_URL = "https://telegram-bot-krill-lotin-krill-translater.onrender.com"

# =========== TOKEN OLISH ===========
def get_token():
    token = os.environ.get("BOT_TOKEN")
    if token:
        return token
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.environ.get("BOT_TOKEN")
        if token:
            return token
    except ImportError:
        pass
    
    print("❌ BOT_TOKEN topilmadi!")
    return None

# =========== BOTNI YARATISH ===========
TOKEN = get_token()
if TOKEN:
    bot = telebot.TeleBot(TOKEN)
    print("✅ Bot yaratildi")
else:
    bot = None
    print("⚠️ BOT_TOKEN yo'q - bot ishga tushmaydi")

# =========== TRANSLITERATION FUNKSIYALARI ===========
try:
    # Ikkala funksiyani ham import qilish
    from uz_trans import to_cyrillic, to_latin, to_latin_simple
    print("✅ Transliteration funksiyalari yuklandi")
    
    # Agar to_latin ishlamasa, to_latin_simple ishlatish
    print("ℹ️ Test: 'ь' ->", to_latin('ь'))
    print("ℹ️ Test: 'щ' ->", to_latin('щ'))
    print("ℹ️ Test: 'ъ' ->", to_latin('ъ'))
    
except Exception as e:
    print(f"❌ uz_trans yuklashda xato: {e}")
    exit(1)

# =========== YORDAMCHI FUNKSIYALAR ===========
def is_admin(user_id):
    """Admin tekshirish - oddiy versiya"""
    return user_id in ADMIN_IDS

def get_all_users():
    """Barcha foydalanuvchilarni olish - oddiy versiya"""
    try:
        users_file = 'users.json'
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def add_user(user_id):
    """Foydalanuvchini qo'shish"""
    try:
        users_file = 'users.json'
        users = get_all_users()
        
        if user_id not in users:
            users.append(user_id)
            
            with open(users_file, 'w') as f:
                json.dump(users, f)
    except:
        pass

# =========== BOT HANDLERS ===========

# 1. START VA YORDAM
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    add_user(message.from_user.id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🌐 Web App", web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)),
        InlineKeyboardButton("❓ Yordam", callback_data="help_info"),
        InlineKeyboardButton("👥 Guruh", callback_data="group_info"),
        InlineKeyboardButton("🌍 Tarjima", callback_data="translate_info"),
        InlineKeyboardButton("📊 Statistika", callback_data="stats_info"),
        InlineKeyboardButton("⭐ Baholash", callback_data="rate_info"),
    ]
    
    # Agar admin bo'lsa, admin tugmasini qo'sh
    if is_admin(message.from_user.id):
        buttons.append(InlineKeyboardButton("⚙️ Admin", callback_data="admin_info"))
    
    # Tugmalarni qatorlarga ajratish
    for i in range(0, len(buttons), 2):
        if i+1 < len(buttons):
            markup.add(buttons[i], buttons[i+1])
        else:
            markup.add(buttons[i])
    
    welcome = f"""
👋 *Assalomu alaykum, {message.from_user.first_name}!*

🤖 *Kirill-Lotin AI Translater Plus* botiga xush kelibsiz!

✨ *Mavjud funksiyalar:*

• Lotin ↔ Kirill avtomatik (cheksiz)
• Tarjima xizmati (18+ til)
• Web App interfeysi
• Fayllarni qabul qilish

*Buyruqlar:* /commands
*Web App:* {WEB_APP_URL}

🚀 *Hammasi bir joyda!*
"""
    bot.send_message(message.chat.id, welcome, parse_mode='Markdown', reply_markup=markup)

# 2. ADMIN PANELI - ISHLAYDI
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bu buyruq faqat adminlar uchun!")
        return
    
    users_count = len(get_all_users())
    
    admin_text = f"""
⚙️ *Admin Panel* 👑

📊 *Statistika:*
• Foydalanuvchilar: {users_count}
• Server: ✅ Faol
• Web App: ✅ Faol

🛠️ *Admin buyruqlari:*
• /broadcast - Barchaga xabar yuborish
• /users - Foydalanuvchilar ro'yxati

📢 *Reklama tarqatish uchun:* /broadcast
"""
    bot.reply_to(message, admin_text, parse_mode='Markdown')

# 3. REKLAMA TARQATISH - ISHLAYDI
@bot.message_handler(commands=['broadcast', 'reklama'])
def broadcast_message(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bu buyruq faqat adminlar uchun!")
        return
    
    msg = bot.reply_to(message, 
        "📢 *Reklama xabarini yuboring:*\n\n"
        "Oddiy matn yoki HTML formatda yuboring.\n"
        "Masalan: <b>Qalin</b>, <i>Yotiq</i>\n\n"
        "Bekor qilish uchun: /cancel",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Reklama bekor qilindi.")
        return
    
    users = get_all_users()
    total_users = len(users)
    
    if total_users == 0:
        bot.reply_to(message, "❌ Hali foydalanuvchilar yo'q.")
        return
    
    bot.reply_to(message, f"📢 Reklama {total_users} foydalanuvchiga yuborilmoqda...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            bot.send_message(
                user_id, 
                f"📢 *Yangilik!*\n\n{message.text}\n\n"
                f"🤖 @translater_krill_latin_krill_bot",
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            success += 1
        except:
            failed += 1
    
    bot.reply_to(
        message, 
        f"✅ *Reklama yuborildi!*\n\n"
        f"✅ Muvaffaqiyatli: {success}\n"
        f"❌ Muvaffaqiyatsiz: {failed}\n\n"
        f"📊 Jami: {total_users} foydalanuvchi",
        parse_mode='Markdown'
    )

# 4. FOYDALANUVCHILAR RO'YXATI
@bot.message_handler(commands=['users'])
def show_users(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bu buyruq faqat adminlar uchun!")
        return
    
    users = get_all_users()
    
    if not users:
        bot.reply_to(message, "❌ Hali foydalanuvchilar yo'q.")
        return
    
    users_text = f"""
👥 *Foydalanuvchilar ro'yxati:*
Jami: {len(users)} ta

*Oxirgi 20 ta foydalanuvchi:*
"""
    
    for i, user_id in enumerate(users[-20:], 1):
        try:
            user_info = bot.get_chat(user_id)
            username = f"@{user_info.username}" if user_info.username else user_info.first_name
            users_text += f"{i}. {username} (ID: {user_id})\n"
        except:
            users_text += f"{i}. ID: {user_id}\n"
    
    bot.reply_to(message, users_text, parse_mode='Markdown')

# 5. TARJIMA XIZMATI
try:
    from deep_translator import GoogleTranslator
    
    LANGUAGES = {
        '🇺🇿 Uzbek': 'uz',
        '🇷🇺 Russian': 'ru', 
        '🇺🇸 English': 'en',
        '🇹🇷 Turkish': 'tr',
        '🇰🇿 Kazakh': 'kk',
        '🇸🇦 Arabic': 'ar',
        '🇨🇳 Chinese': 'zh-CN',
        '🇰🇷 Korean': 'ko',
        '🇯🇵 Japanese': 'ja',
        '🇩🇪 German': 'de',
        '🇫🇷 French': 'fr',
        '🇪🇸 Spanish': 'es',
    }
    
    @bot.message_handler(commands=['translate'])
    def translate_command(message):
        markup = InlineKeyboardMarkup(row_width=2)
        
        buttons = []
        for lang_name, lang_code in LANGUAGES.items():
            btn = InlineKeyboardButton(lang_name, callback_data=f"translate_{lang_code}")
            buttons.append(btn)
        
        for i in range(0, len(buttons), 2):
            if i+1 < len(buttons):
                markup.add(buttons[i], buttons[i+1])
            else:
                markup.add(buttons[i])
        
        help_text = """
🌍 *Tarjima xizmati*

1. Tugmalardan tilni tanlang
2. Tarjima qilish uchun matn yuboring

✨ *Qo'llab-quvvatlanadigan tillar:* 12+ til
"""
        bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=markup)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('translate_'))
    def translate_callback(call):
        lang_code = call.data.split('_')[1]
        
        lang_name = "noma'lum"
        for name, code in LANGUAGES.items():
            if code == lang_code:
                lang_name = name
                break
        
        msg = bot.send_message(
            call.message.chat.id, 
            f"🌍 *Tanlangan til:* {lang_name}\n\nTarjima qilish uchun matn yuboring:",
            parse_mode='Markdown'
        )
        
        bot.register_next_step_handler(msg, process_translation, lang_code, lang_name)
        bot.answer_callback_query(call.id)
    
    def process_translation(message, lang_code, lang_name):
        try:
            text = message.text
            
            if not text.strip():
                bot.reply_to(message, "❌ Matn yuboring!")
                return
            
            translator = GoogleTranslator(source='auto', target=lang_code)
            translated_text = translator.translate(text)
            
            response = f"""
🌐 *Tarjima natijasi:*

🔤 *{lang_name}:*
`{translated_text}`

📝 *Asl matn:*
`{text}`

💬 *Uzunligi:* {len(text)} → {len(translated_text)} belgi
"""
            bot.reply_to(message, response, parse_mode='Markdown')
            
        except Exception as e:
            bot.reply_to(message, f"❌ Tarjimada xato: {str(e)[:100]}")

except ImportError:
    @bot.message_handler(commands=['translate'])
    def translate_command(message):
        bot.reply_to(message, "❌ Tarjima xizmati hozircha mavjud emas.")

# 6. ASOSIY KONVERTATSIYA
@bot.message_handler(func=lambda message: True)
def convert_text(message):
    """Asosiy konvertatsiya funksiyasi"""
    text = message.text
    
    if text.startswith('/'):
        return
    
    try:
        add_user(message.from_user.id)
        
        if any('\u0400' <= char <= '\u04FF' for char in text):
            converted = to_latin(text)
            direction = "Kirill → Lotin"
        else:
            converted = to_cyrillic(text)
            direction = "Lotin → Kirill"
        
        response_text = f"""
*{direction}:*

`{converted}`

📏 *Uzunligi:* {len(text):,} belgi

🔗 *Ulashish:* /share
🌍 *Tarjima:* /translate
"""
        bot.reply_to(message, response_text, parse_mode='Markdown')
        
    except Exception as e:
        error_text = f"❌ *Xatolik yuz berdi:*\n\n`{str(e)[:200]}`"
        bot.reply_to(message, error_text, parse_mode='Markdown')

# 7. CALLBACK HANDLERS
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "help_info":
        help_text = """
🆘 *Qanday ishlatish?*

*Bot orqali:*
1. Faqat matn yuboring
2. Bot avtomatik aniqlab konvertatsiya qiladi

*Tarjima orqali:*
1. /translate buyrug'ini bosing
2. Tugmalardan tilni tanlang
3. Matn yuboring

*Qo'shimcha:*
• /admin - Admin paneli (faqat admin)
• /broadcast - Reklama tarqatish (faqat admin)
"""
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, help_text, parse_mode='Markdown')
    
    elif call.data == "group_info":
        group_text = """
👥 *Guruhga qo'shish*

Botni guruhga qo'shishingiz mumkin:
@translater_krill_latin_krill_bot

✨ *Guruhda ishlash:*
• Odamlar matn yuborsa, bot avtomatik javob beradi
"""
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, group_text, parse_mode='Markdown')
    
    elif call.data == "translate_info":
        bot.answer_callback_query(call.id)
        translate_command(call.message)
    
    elif call.data == "stats_info":
        users_count = len(get_all_users())
        stats_text = f"""
📊 *Bot statistikasi:*

• Foydalanuvchilar: {users_count}
• Server: ✅ Faol
• Web App: ✅ Faol
"""
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, stats_text, parse_mode='Markdown')
    
    elif call.data == "rate_info":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("⭐ 5 yulduz", callback_data="rate_5"),
            InlineKeyboardButton("🔗 Ulashish", url="https://t.me/share/url?url=https://t.me/translater_krill_latin_krill_bot&text=Ajoyib bot!")
        )
        
        rate_text = """
⭐ *Botni baholang*

Agar bot sizga yoqgan bo'lsa:
• Baholang
• Do'stlaringizga ulashing

🤝 *Dasturchi:* @Boboxon_Jumaboyev
"""
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, rate_text, parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "admin_info":
        if is_admin(call.from_user.id):
            bot.answer_callback_query(call.id)
            admin_panel(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Bu tugma faqat adminlar uchun!", show_alert=True)
    
    elif call.data.startswith("rate_"):
        rating = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"✅ {rating} yulduz uchun rahmat! 🙏", show_alert=True)

# 8. BOSHQA BUYRUQLAR
@bot.message_handler(commands=['test'])
def test_bot(message):
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

@bot.message_handler(commands=['webapp'])
def send_webapp_link(message):
    markup = InlineKeyboardMarkup()
    
    web_app_btn = InlineKeyboardButton(
        "🌐 Web App'ni ochish", 
        web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)
    )
    
    markup.add(web_app_btn)
    
    bot.send_message(
        message.chat.id,
        f"🌐 *Web App manzili:*\n\n{WEB_APP_URL}",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['commands'])
def commands_list(message):
    commands_text = """
📋 *Mavjud buyruqlar:*

• /start, /help - Botni ishga tushirish
• /test - Botni test qilish
• /webapp - Web App manzili
• /translate - Tarjima xizmati
• /users - Foydalanuvchilar (admin)
• /admin - Admin paneli (admin)
• /broadcast - Reklama (admin)
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

# =========== BOTNI ISHGA TUSHIRISH ===========
def start_bot():
    """Start polling the Telegram bot. Designed to be run in a background thread.

    Returns immediately if BOT_TOKEN is not configured.
    """
    if bot is None:
        print("⚠️ BOT_TOKEN yo'q - bot ishga tushmaydi")
        return

    print("\n" + "="*50)
    print("🚀 BOT ISHGA TUSHMOQDA...")
    print(f"🤖 Bot: @translater_krill_latin_krill_bot")
    print(f"🌐 Web App: {WEB_APP_URL}")
    print(f"👑 Admin ID: {ADMIN_IDS}")
    print("="*50)

    # Start polling with basic retry loop to survive transient errors
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"❌ Botda xato: {e}")
            # Backoff before restarting polling
            import time
            time.sleep(5)