# stats.py - PANDAS SIZ VERSIYA
from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# =========== YORDAMCHI FUNKSIYALAR ===========

def get_stats():
    """Statistikani o'qish"""
    try:
        stats_file = 'data/stats.json'
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Stats o'qishda xato: {e}")
    
    # Boshlang'ich statistikalar
    return {
        "total_conversions": 0,
        "total_characters": 0,
        "total_files": 0,
        "total_translations": 0,
        "users": [],
        "daily_stats": {},
        "hourly_stats": {},
        "top_users": []
    }

def save_stats(stats):
    """Statistikani saqlash"""
    try:
        # Papka mavjudligini tekshirish
        os.makedirs('data', exist_ok=True)
        
        stats_file = 'data/stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Stats saqlashda xato: {e}")
        return False

def update_stats(action_type, user_id=None, characters=0):
    """Statistikani yangilash (pandas siz)"""
    stats = get_stats()
    
    # Asosiy statistika
    stats["total_conversions"] = stats.get("total_conversions", 0) + 1
    stats["total_characters"] = stats.get("total_characters", 0) + characters
    
    # Harakat turi bo'yicha
    if action_type == "file":
        stats["total_files"] = stats.get("total_files", 0) + 1
    elif action_type == "translation":
        stats["total_translations"] = stats.get("total_translations", 0) + 1
    
    # Foydalanuvchi qo'shish
    if user_id and str(user_id) not in stats.get("users", []):
        stats.setdefault("users", []).append(str(user_id))
    
    # Kunlik statistika
    today = datetime.now().strftime("%Y-%m-%d")
    hour = datetime.now().strftime("%H:00")
    
    # Daily stats
    daily_stats = stats.setdefault("daily_stats", {})
    if today not in daily_stats:
        daily_stats[today] = {
            "conversions": 0,
            "characters": 0,
            "users": [],
            "files": 0,
            "translations": 0
        }
    
    daily_stats[today]["conversions"] += 1
    daily_stats[today]["characters"] += characters
    
    if action_type == "file":
        daily_stats[today]["files"] += 1
    elif action_type == "translation":
        daily_stats[today]["translations"] += 1
    
    if user_id and str(user_id) not in daily_stats[today]["users"]:
        daily_stats[today]["users"].append(str(user_id))
    
    # Soatlik statistika
    hourly_stats = stats.setdefault("hourly_stats", {})
    hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
    
    # Top foydalanuvchilar
    update_top_users(stats, user_id)
    
    # Saqlash
    save_stats(stats)
    return stats

def update_top_users(stats, user_id):
    """Top foydalanuvchilarni yangilash (pandas siz)"""
    if not user_id:
        return
    
    user_id_str = str(user_id)
    top_users = stats.setdefault("top_users", [])
    
    # Foydalanuvchini topish
    user_found = False
    for user in top_users:
        if user["id"] == user_id_str:
            user["count"] = user.get("count", 0) + 1
            user_found = True
            break
    
    # Yangi foydalanuvchi
    if not user_found:
        top_users.append({
            "id": user_id_str,
            "count": 1,
            "first_seen": datetime.now().strftime("%Y-%m-%d")
        })
    
    # Saralash (pandas siz)
    stats["top_users"] = sorted(top_users, 
                               key=lambda x: x["count"], 
                               reverse=True)[:10]

# =========== FLASK ROUTES ===========

@app.route('/')
def index():
    """Asosiy statistika sahifasi"""
    stats = get_stats()
    
    # To'plangan ma'lumotlar
    total_conversions = stats.get("total_conversions", 0)
    total_users = len(stats.get("users", []))
    total_characters = stats.get("total_characters", 0)
    total_files = stats.get("total_files", 0)
    total_translations = stats.get("total_translations", 0)
    
    # Oxirgi 7 kun statistikasi
    daily_stats = stats.get("daily_stats", {})
    
    # Kunlarni saralash (pandas siz)
    sorted_days = sorted(daily_stats.items(), key=lambda x: x[0], reverse=True)
    last_7_days = sorted_days[:7]
    
    # Soatlik statistika (oxirgi 24 soat)
    hourly_stats = stats.get("hourly_stats", {})
    
    # Soatlarni saralash (pandas siz)
    sorted_hours = sorted(hourly_stats.items(), key=lambda x: x[0], reverse=True)
    last_24_hours = sorted_hours[:24]
    
    # Top foydalanuvchilar
    top_users = stats.get("top_users", [])[:5]
    
    # Platforma ma'lumotlari
    platform_info = {
        "bot_url": "https://t.me/translater_krill_latin_krill_bot",
        "webapp_url": "https://telegram-bot-krill-lotin-krill-translater.onrender.com",
        "start_time": "2024-01-01",
        "uptime": "99.9%",
        "version": "2.0.0"
    }
    
    return render_template('stats_dashboard.html',
                         total_conversions=total_conversions,
                         total_users=total_users,
                         total_characters=total_characters,
                         total_files=total_files,
                         total_translations=total_translations,
                         daily_stats=last_7_days,
                         hourly_stats=last_24_hours,
                         top_users=top_users,
                         platform_info=platform_info)

@app.route('/api/stats')
def api_stats():
    """API: To'liq statistika"""
    stats = get_stats()
    return jsonify({
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/daily')
def api_daily():
    """API: Kunlik statistika"""
    stats = get_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    
    daily_data = stats.get("daily_stats", {}).get(today, {
        "conversions": 0,
        "characters": 0,
        "users": [],
        "files": 0,
        "translations": 0
    })
    
    return jsonify({
        "success": True,
        "date": today,
        "data": daily_data
    })

@app.route('/api/hourly')
def api_hourly():
    """API: Soatlik statistika"""
    stats = get_stats()
    
    # Oxirgi 24 soat (pandas siz)
    last_24_hours = {}
    now = datetime.now()
    
    for i in range(24):
        hour_time = now - timedelta(hours=i)
        hour_key = hour_time.strftime("%H:00")
        last_24_hours[hour_key] = stats.get("hourly_stats", {}).get(hour_key, 0)
    
    # Saralash
    sorted_hours = dict(sorted(last_24_hours.items(), reverse=True))
    
    return jsonify({
        "success": True,
        "data": sorted_hours
    })

@app.route('/api/update', methods=['POST'])
def api_update():
    """API: Statistikani yangilash (bot uchun)"""
    try:
        from flask import request
        
        data = request.json
        action_type = data.get("action", "conversion")
        user_id = data.get("user_id")
        characters = data.get("characters", 0)
        
        stats = update_stats(action_type, user_id, characters)
        
        return jsonify({
            "success": True,
            "message": "Statistika yangilandi",
            "total_conversions": stats["total_conversions"]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

# =========== STATIC FILES ===========

@app.route('/static/<path:path>')
def serve_static(path):
    """Static fayllarni server qilish"""
    return send_from_directory('static', path)

# =========== ERROR HANDLERS ===========

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Sahifa topilmadi"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server xatosi"}), 500

# =========== MAIN ===========

if __name__ == '__main__':
    # Data papkasini yaratish
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("📊 Statistika serveri ishga tushmoqda...")
    print("🌐 Dashboard: http://localhost:5001")
    print("📈 API: http://localhost:5001/api/stats")
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)