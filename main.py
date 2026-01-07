# main.py - TO'LIQ VERSIYA BARCHA FUNKSIYALAR BILAN
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
ADMIN_IDS = [1051632082]  # Faqat sizning ID'ingiz
WEB_APP_URL = "https://telegram-bot-krill-lotin-krill-translater.onrender.com"
HISTORY_FILE = 'history.json'
STATS_FILE = 'stats.json'

# =========== TOKEN OLISH ===========
def get_token():
    """Tokenni xavfsiz olish"""
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
    
    # 3. TOKEN TOPILMADI
    print("❌ XATO: BOT_TOKEN topilmadi!")
    sys.exit(1)

# =========== BOTNI YARATISH ===========
TOKEN = get_token()
bot = telebot.TeleBot(TOKEN)
print("✅ Bot yaratildi")

# =========== TRANSLITERATION FUNKSIYALARI ===========
try:
    with open('uz_trans.py', 'r', encoding='utf-8') as f:
        exec(f.read(), globals())
    print("✅ Transliteration funksiyalari yuklandi")
except Exception as e:
    print(f"❌ uz_trans.py yuklashda xato: {e}")
    exit(1)

# =========== YORDAMCHI FUNKSIYALAR ===========
def is_admin(user_id):
    """Admin tekshirish"""
    return user_id in ADMIN_IDS

def update_stats(user_id, action="conversion"):
    """Statistikani yangilash"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
        else:
            stats = {"total_conversions": 0, "users": {}, "actions": {}}
        
        stats["total_conversions"] = stats.get("total_conversions", 0) + 1
        
        user_key = str(user_id)
        if user_key not in stats["users"]:
            stats["users"][user_key] = 0
        stats["users"][user_key] += 1
        
        # Harakatlar statistikasi
        if action not in stats["actions"]:
            stats["actions"][action] = 0
        stats["actions"][action] += 1
        
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f)
    except:
        pass

def save_history(user_id, original, converted, direction):
    """Tarixni saqlash"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {}
        
        user_key = str(user_id)
        if user_key not in history:
            history[user_key] = []
        
        history[user_key].append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original": original[:100],
            "converted": converted[:100],
            "direction": direction
        })
        
        if len(history[user_key]) > 10:
            history[user_key] = history[user_key][-10:]
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass

# =========== BOT HANDLERS ===========

# 1. START VA YORDAM (ADMIN UCHUN MAXSUS TUGMALAR)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Har bir foydalanuvchi uchun asosiy tugmalar
    buttons = [
        InlineKeyboardButton("🌐 Web App", web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)),
        InlineKeyboardButton("❓ Yordam", callback_data="help_info"),
        InlineKeyboardButton("👥 Guruh", callback_data="group_info"),
        InlineKeyboardButton("📜 Tarix", callback_data="history_info"),
        InlineKeyboardButton("📁 Fayl", callback_data="file_info"),
        InlineKeyboardButton("🌍 Tarjima", callback_data="translate_info"),
        InlineKeyboardButton("📊 Statistika", callback_data="stats_info"),
        InlineKeyboardButton("🤝 Reklama", callback_data="advert_info"),
        InlineKeyboardButton("⭐ Baholash", url="https://t.me/translater_krill_latin_krill_bot?start=rate"),
        InlineKeyboardButton("🔗 Ulashish", url=f"https://t.me/share/url?url=https://t.me/translater_krill_latin_krill_bot&text=Kirill-Lotin konvertatsiya boti")
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

1️⃣ *Asosiy konvertatsiya:*
   • Lotin ↔ Kirill avtomatik
   • Faqat matn yuboring

2️⃣ *Yangi funksiyalar:*
   • 📁 Fayllarni qabul qilish (.txt)
   • 📜 Konvertatsiya tarixi
   • 👥 Guruhlar uchun
   • 🌍 Tarjima xizmati
   • 📊 Statistika

3️⃣ *Web App:*
   • Chiroyli interfeys
   • Natijani nusxalash
   • Tugmalar orqali oson ishlash

*Buyruqlar:* /commands
*Web App:* {WEB_APP_URL}

🚀 *Hammasi bir joyda!*
"""
    bot.send_message(message.chat.id, welcome, parse_mode='Markdown', reply_markup=markup)
    update_stats(message.from_user.id, "start")

# 2. BUYRUQLAR RO'YXATI
@bot.message_handler(commands=['commands'])
def commands_list(message):
    commands_text = """
📋 *Mavjud buyruqlar:*

*Asosiy:*
• /start, /help - Botni ishga tushirish
• /test - Botni test qilish
• /webapp - Web App manzili

*Yangi funksiyalar:*
• /group - Guruhga qo'shish
• /history - Konvertatsiya tarixi
• /stats - Statistika
• /translate - Tarjima xizmati
• /feedback - Fikr-mulohaza
• /advert - Reklama tarqatish

*Admin uchun:*
• /admin - Admin paneli
• /broadcast - Xabar yuborish

📁 *Fayl yuborish:* 
Faqat .txt fayl yuboring
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

# 3. WEB APP
@bot.message_handler(commands=['webapp'])
def send_webapp_link(message):
    markup = InlineKeyboardMarkup()
    
    web_app_btn = InlineKeyboardButton(
        "🌐 Web App'ni ochish", 
        web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)
    )
    
    open_in_browser = InlineKeyboardButton(
        "🔗 Brauzerda ochish",
        url=WEB_APP_URL
    )
    
    markup.add(web_app_btn)
    markup.add(open_in_browser)
    
    bot.send_message(
        message.chat.id,
        f"🌐 *Web App manzili:*\n\n`{WEB_APP_URL}`",
        parse_mode='Markdown',
        reply_markup=markup
    )

# 4. GURUHLAR UCHUN
@bot.message_handler(commands=['group'])
def group_info(message):
    group_text = """
👥 *Guruhga qo'shish*

Botni guruhga qo'shishingiz mumkin:

1️⃣ Guruh sozlamalariga boring
2️⃣ "Administratorlar" ni tanlang  
3️⃣ "Administrator qo'shish" dan botni qidiring:
   @translater_krill_latin_krill_bot
4️⃣ Quyidagi huquqlarni bering:
   ✅ Xabarlar yuborish
   ✅ Matnlarni o'qish
   ❌ Boshqa huquqlar (shart emas)

✨ *Guruhda ishlash:*
• Odamlar matn yuborsa, bot avtomatik javob beradi
• /help - yordam ko'rsatadi
• /webapp - Web App haqida
• /commands - buyruqlar ro'yxati

📢 *Reklama tarqatish:* /advert
"""
    bot.reply_to(message, group_text, parse_mode='Markdown')

# 5. TARIX
@bot.message_handler(commands=['history'])
def show_history(message):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            user_key = str(message.from_user.id)
            if user_key in history and history[user_key]:
                history_text = "📜 *Oxirgi 10 ta konvertatsiya:*\n\n"
                
                for i, item in enumerate(reversed(history[user_key]), 1):
                    history_text += f"▫️ *{item['direction']}*\n"
                    history_text += f"   ⏰ {item['time']}\n"
                    history_text += f"   Kiruvchi: {item['original']}...\n"
                    history_text += f"   Natija: {item['converted']}...\n\n"
                
                bot.reply_to(message, history_text, parse_mode='Markdown')
            else:
                bot.reply_to(message, "📜 Tarix bo'sh. Avval konvertatsiya qiling!")
        else:
            bot.reply_to(message, "📜 Tarix bo'sh. Avval konvertatsiya qiling!")
    except:
        bot.reply_to(message, "❌ Tarixni o'qishda xato!")

# 6. STATISTIKA
@bot.message_handler(commands=['stats'])
def show_stats(message):
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
        else:
            stats = {"total_conversions": 0, "users": {}, "actions": {}}
        
        total = stats.get("total_conversions", 0)
        users = len(stats.get("users", {}))
        
        # Top 5 foydalanuvchi
        top_users = sorted(
            stats.get("users", {}).items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        stats_text = f"""
📊 *Bot statistikasi:*

• Jami konvertatsiyalar: {total}
• Foydalanuvchilar soni: {users}
• Server holati: ✅ Faol
• Web App: ✅ Faol

🏆 *Top 5 foydalanuvchi:*
"""
        for i, (user_id, count) in enumerate(top_users, 1):
            stats_text += f"{i}. ID: {user_id[:8]}... - {count} marta\n"
        
        bot.reply_to(message, stats_text, parse_mode='Markdown')
    except:
        bot.reply_to(message, "📊 Statistika hali to'planmagan")

# 7. FAYL QABUL QILISH
@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = message.document.file_name
        file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        if file_ext not in ['txt']:
            bot.reply_to(message, "❌ Faqat .txt fayllarni qabul qilamiz!")
            return
        
        # Faylni saqlash
        temp_file = f"temp_{uuid.uuid4()}.{file_ext}"
        with open(temp_file, 'wb') as f:
            f.write(downloaded_file)
        
        # Faylni o'qish
        with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if len(content) > 5000:
            bot.reply_to(message, "❌ Fayl juda katta (5000 belgidan oshmasin)")
            os.remove(temp_file)
            return
        
        # Konvertatsiya
        if any('\u0400' <= char <= '\u04FF' for char in content):
            converted = to_latin(content)
            direction = "Kirill → Lotin"
        else:
            converted = to_cyrillic(content)
            direction = "Lotin → Kirill"
        
        # Natijani faylga yozish
        result_file = f"converted_{file_name}"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(converted)
        
        # Yuborish
        with open(result_file, 'rb') as f:
            bot.send_document(
                message.chat.id, 
                f, 
                caption=f"✅ {direction}\n📁 Fayl: {file_name}\n📏 Uzunlik: {len(content)} belgi"
            )
        
        # Tozalash
        os.remove(temp_file)
        os.remove(result_file)
        
        update_stats(message.from_user.id, "file_conversion")
        save_history(message.from_user.id, content[:50], converted[:50], direction)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Xato: {str(e)[:100]}")

# 8. TARJIMA XIZMATI - TIL KODLARINI TUZATAMIZ
try:
    from deep_translator import GoogleTranslator
    
    # TO'G'RI TIL KODLARI
    LANGUAGES = {
        '🇺🇿 Uzbek': 'uz',
        '🇷🇺 Russian': 'ru', 
        '🇺🇸 English': 'en',
        '🇹🇷 Turkish': 'tr',
        '🇰🇿 Kazakh': 'kk',
        '🇸🇦 Arabic': 'ar',
        '🇨🇳 Chinese': 'zh-cn',
        '🇰🇷 Korean': 'ko',
        '🇯🇵 Japanese': 'ja',
        '🇩🇪 German': 'de',
        '🇫🇷 French': 'fr',
        '🇪🇸 Spanish': 'es'
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
🌍 *Tarjima qilish*

1. Matn yuboring (1000 belgigacha)
2. Tugmalardan tilni tanlang
3. Bot tarjima qiladi

✨ *Qo'llab-quvvatlanadigan tillar:*
• Uzbek, Russian, English
• Turkish, Kazakh, Arabic
• Chinese, Korean, Japanese
• German, French, Spanish
"""
        bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=markup)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('translate_'))
    def translate_callback(call):
        lang_code = call.data.split('_')[1]
        
        # Til nomini topish
        lang_name = "noma'lum"
        for name, code in LANGUAGES.items():
            if code == lang_code:
                lang_name = name
                break
        
        msg = bot.send_message(
            call.message.chat.id, 
            f"🌍 Tanlangan til: {lang_name}\n\nTarjima qilish uchun matn yuboring (1000 belgigacha):"
        )
        
        bot.register_next_step_handler(msg, process_translation, lang_code, lang_name)
        bot.answer_callback_query(call.id)
    
    def process_translation(message, lang_code, lang_name):
        try:
            text = message.text[:1000]  # 1000 belgigacha
            
            if not text.strip():
                bot.reply_to(message, "❌ Matn yuboring!")
                return
            
            translator = GoogleTranslator(source='auto', target=lang_code)
            translated = translator.translate(text)
            
            # Manba tilni aniqlash
            try:
                source_lang = GoogleTranslator(source='auto', target='en').detect(text)
            except:
                source_lang = "auto"
            
            response = f"""
🌐 *Tarjima natijasi:*

📝 *Asl matn ({source_lang}):*
`{text}`

🔤 *Tarjima ({lang_name}):*
`{translated}`

💬 *Uzunligi:* {len(text)} → {len(translated)} belgi

⭐ *Botni baholang:* /rate
"""
            bot.reply_to(message, response, parse_mode='Markdown')
            update_stats(message.from_user.id, "translation")
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                bot.reply_to(message, "❌ Tarjima limiti tugagan. Iltimos, keyinroq urinib ko'ring.")
            else:
                bot.reply_to(message, f"❌ Tarjimada xato: {error_msg[:100]}")

except ImportError:
    @bot.message_handler(commands=['translate'])
    def translate_command(message):
        bot.reply_to(message, "❌ Tarjima xizmati hozircha mavjud emas. requirements.txt ga 'deep-translator' qo'shing.")

# 9. ADMIN PANELI - FAQAT ADMINLAR UCHUN
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bu buyruq faqat adminlar uchun!")
        return
    
    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
    except:
        stats = {"total_conversions": 0, "users": {}, "actions": {}}
    
    total = stats.get("total_conversions", 0)
    users = len(stats.get("users", {}))
    
    admin_text = f"""
⚙️ *Admin Panel* 👑

📊 *Statistika:*
• Jami konvertatsiyalar: {total}
• Foydalanuvchilar soni: {users}
• Server: ✅ Faol
• Web App: ✅ Faol

🛠️ *Admin buyruqlari:*
• /broadcast - Barchaga xabar yuborish
• /advert - Reklama tarqatish
• /stats_full - To'liq statistika

📢 *Reklama tarqatish uchun:* /advert
"""
    bot.reply_to(message, admin_text, parse_mode='Markdown')

# 10. REKLAMA TARQATISH - FAQAT ADMIN
@bot.message_handler(commands=['advert', 'broadcast'])
def advert_message(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bu buyruq faqat adminlar uchun!")
        return
    
    msg = bot.reply_to(message, 
        "📢 *Reklama xabarini yuboring:*\n\n"
        "Xabar formatida yuboring. HTML teglari ishlaydi.\n"
        "Masalan: <b>Qalin</b>, <i>Yotiq</i>, <a href='link'>Havola</a>",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_advert)

def process_advert(message):
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
            
            users = list(stats.get("users", {}).keys())
            success = 0
            failed = 0
            
            bot.reply_to(message, f"📢 Reklama {len(users)} foydalanuvchiga yuborilmoqda...")
            
            for user_id in users:
                try:
                    bot.send_message(
                        user_id, 
                        f"📢 *Bot yangiligi:*\n\n{message.text}\n\n"
                        f"🤖 @translater_krill_latin_krill_bot",
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    success += 1
                    
                    # Har 10 ta xabardan keyin kutish
                    if success % 10 == 0:
                        import time
                        time.sleep(1)
                        
                except Exception as e:
                    failed += 1
            
            bot.reply_to(
                message, 
                f"✅ *Reklama yuborildi!*\n\n"
                f"✅ Muvaffaqiyatli: {success}\n"
                f"❌ Muvaffaqiyatsiz: {failed}\n\n"
                f"📊 Jami: {len(users)} foydalanuvchi",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(message, "❌ Statistika fayli topilmadi")
    except Exception as e:
        bot.reply_to(message, f"❌ Xato: {str(e)}")

# 11. BAHOLASH VA ULASHISH
@bot.message_handler(commands=['rate', 'share'])
def rate_share(message):
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("⭐ 5 yulduz", callback_data="rate_5"),
        InlineKeyboardButton("⭐ 4 yulduz", callback_data="rate_4"),
        InlineKeyboardButton("⭐ 3 yulduz", callback_data="rate_3"),
        InlineKeyboardButton("🔗 Do'stga ulash", url=f"https://t.me/share/url?url=https://t.me/translater_krill_latin_krill_bot&text=Kirill-Lotin konvertatsiya boti"),
        InlineKeyboardButton("👥 Guruhga qo'sh", callback_data="add_to_group"),
        InlineKeyboardButton("📢 Reklama", callback_data="advert_request")
    ]
    
    markup.add(*buttons[:2])
    markup.add(*buttons[2:4])
    markup.add(*buttons[4:])
    
    rate_text = """
⭐ *Botni baholang*

Agar bot sizga yoqgan bo'lsa:
• Baholang
• Do'stlaringizga ulashing
• Guruhga qo'shing

🤝 *Dasturchi:* @Boboxon_Jumaboyev
"""
    bot.reply_to(message, rate_text, parse_mode='Markdown', reply_markup=markup)

# 12. ASOSIY KONVERTATSIYA
@bot.message_handler(func=lambda message: True)
def convert_text(message):
    """Asosiy konvertatsiya funksiyasi"""
    text = message.text
    
    if text.startswith('/'):
        return
    
    # Uzun matn tekshiruvi
    if len(text) > 2000:
        bot.reply_to(message, "❌ Matn juda uzun (2000 belgidan oshmasin)")
        return
    
    try:
        # Matn kirill yoki lotin ekanligini aniqlash
        if any('\u0400' <= char <= '\u04FF' for char in text):
            converted = to_latin(text)
            direction = "Kirill → Lotin"
        else:
            converted = to_cyrillic(text)
            direction = "Lotin → Kirill"
        
        response_text = f"""
{direction}:

`{converted}`

📏 *Uzunlik:* {len(text)} → {len(converted)} belgi

⭐ *Botni baholang:* /rate
🔗 *Ulashish:* /share
"""
        bot.reply_to(message, response_text, parse_mode='Markdown')
        
        # Statistikani yangilash
        update_stats(message.from_user.id)
        save_history(message.from_user.id, text[:50], converted[:50], direction)
        
    except Exception as e:
        error_text = f"❌ *Xatolik yuz berdi:*\n\n`{str(e)[:100]}`"
        bot.reply_to(message, error_text, parse_mode='Markdown')

# 13. CALLBACK HANDLERS - BARCHA TUGMALAR
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # Yordam
    if call.data == "help_info":
        help_text = """
🆘 *Qanday ishlatish?*

*Bot orqali:*
1. Faqat matn yuboring
2. Bot avtomatik aniqlab konvertatsiya qiladi

*Fayl orqali:*
1. .txt fayl yuboring
2. Bot avtomatik konvertatsiya qiladi

*Web App orqali:*
1. "🌐 Web App" tugmasini bosing
2. Matnni kiritish maydoniga yozing
3. Tugmalar orqali konvertatsiya qiling

*Qo'shimcha:*
• /history - Tarixni ko'rish
• /stats - Statistika
• /translate - Tarjima xizmati
• /rate - Botni baholash
"""
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, help_text, parse_mode='Markdown')
    
    # Guruh
    elif call.data == "group_info":
        bot.answer_callback_query(call.id)
        group_info(call.message)
    
    # Tarix
    elif call.data == "history_info":
        bot.answer_callback_query(call.id)
        show_history(call.message)
    
    # Statistika
    elif call.data == "stats_info":
        bot.answer_callback_query(call.id)
        show_stats(call.message)
    
    # Fayl
    elif call.data == "file_info":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 
            "📁 *Fayl yuborish:*\n\nFaqat .txt fayl yuboring. Bot avtomatik konvertatsiya qiladi.\n\nMaksimal hajm: 5000 belgi",
            parse_mode='Markdown')
    
    # Tarjima
    elif call.data == "translate_info":
        bot.answer_callback_query(call.id)
        translate_command(call.message)
    
    # Reklama (barcha uchun)
    elif call.data == "advert_info":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
            "📢 *Reklama tarqatish*\n\n"
            "Bot haqida do'stlaringizga gapirib bering:\n\n"
            "1. Botni baholang: /rate\n"
            "2. Do'stlarga ulashing: /share\n"
            "3. Guruhga qo'shing: /group\n\n"
            "🤝 *Dasturchi:* @Boboxon_Jumaboyev",
            parse_mode='Markdown')
    
    # Admin paneli (faqat admin uchun)
    elif call.data == "admin_info":
        if is_admin(call.from_user.id):
            bot.answer_callback_query(call.id)
            admin_panel(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Bu tugma faqat adminlar uchun!", show_alert=True)
    
    # Baholash
    elif call.data.startswith("rate_"):
        rating = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"✅ {rating} yulduz uchun rahmat!", show_alert=True)
        
        # Baholash statistikasini saqlash
        try:
            rating_file = 'ratings.json'
            if os.path.exists(rating_file):
                with open(rating_file, 'r') as f:
                    ratings = json.load(f)
            else:
                ratings = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
            
            if rating in ratings:
                ratings[rating] += 1
            
            with open(rating_file, 'w') as f:
                json.dump(ratings, f)
        except:
            pass
    
    # Guruhga qo'shish
    elif call.data == "add_to_group":
        bot.answer_callback_query(call.id)
        group_info(call.message)
    
    # Reklama so'rovi
    elif call.data == "advert_request":
        bot.answer_callback_query(call.id)
        advert_message(call.message)

# 14. TEST BUYRUQ'I
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

⭐ *Botni baholang:* /rate
"""
        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Testda xato: {str(e)}")

# 15. FEEDBACK
@bot.message_handler(commands=['feedback'])
def feedback_command(message):
    feedback_text = """
📝 *Fikr-mulohaza*

Agar taklif yoki shikoyatingiz bo'lsa:
• @Boboxon_Jumaboyev ga yozing
• Yoki shu yerda yozib qoldiring

Botni yaxshilashda yordamingiz uchun rahmat! 🙏
"""
    bot.reply_to(message, feedback_text, parse_mode='Markdown')

# =========== BOTNI ISHGA TUSHIRISH ===========
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 BOT ISHGA TUSHMOQDA...")
    print(f"🤖 Bot: @translater_krill_latin_krill_bot")
    print(f"🌐 Web App: {WEB_APP_URL}")
    print(f"👑 Admin ID: {ADMIN_IDS}")
    print("="*50)
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Botda xato: {e}")