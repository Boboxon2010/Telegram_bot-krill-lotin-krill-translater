# stats.py - TO'LIQ STATISTIKA SERVERI
from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
import threading
import time

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
    """Statistikani yangilash"""
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
    if user_id and user_id not in stats.get("users", []):
        stats["users"] = stats.get("users", [])
        stats["users"].append(str(user_id))
    
    # Kunlik statistika
    today = datetime.now().strftime("%Y-%m-%d")
    hour = datetime.now().strftime("%H:00")
    
    # Daily stats
    if "daily_stats" not in stats:
        stats["daily_stats"] = {}
    
    if today not in stats["daily_stats"]:
        stats["daily_stats"][today] = {
            "conversions": 0,
            "characters": 0,
            "users": [],
            "files": 0,
            "translations": 0
        }
    
    stats["daily_stats"][today]["conversions"] += 1
    stats["daily_stats"][today]["characters"] += characters
    
    if action_type == "file":
        stats["daily_stats"][today]["files"] += 1
    elif action_type == "translation":
        stats["daily_stats"][today]["translations"] += 1
    
    if user_id and str(user_id) not in stats["daily_stats"][today]["users"]:
        stats["daily_stats"][today]["users"].append(str(user_id))
    
    # Soatlik statistika
    if "hourly_stats" not in stats:
        stats["hourly_stats"] = {}
    
    if hour not in stats["hourly_stats"]:
        stats["hourly_stats"][hour] = 0
    
    stats["hourly_stats"][hour] += 1
    
    # Top foydalanuvchilar
    update_top_users(stats, user_id)
    
    # Saqlash
    save_stats(stats)
    return stats

def update_top_users(stats, user_id):
    """Top foydalanuvchilarni yangilash"""
    if not user_id:
        return
    
    user_id_str = str(user_id)
    
    # Top users array mavjudligini tekshirish
    if "top_users" not in stats:
        stats["top_users"] = []
    
    # Foydalanuvchini topish yoki qo'shish
    user_found = False
    for user in stats["top_users"]:
        if user["id"] == user_id_str:
            user["count"] = user.get("count", 0) + 1
            user_found = True
            break
    
    if not user_found:
        stats["top_users"].append({
            "id": user_id_str,
            "count": 1,
            "first_seen": datetime.now().strftime("%Y-%m-%d")
        })
    
    # Sort by count (descending)
    stats["top_users"] = sorted(stats["top_users"], 
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
    last_7_days = sorted(daily_stats.items(), reverse=True)[:7]
    
    # Soatlik statistika (oxirgi 24 soat)
    hourly_stats = stats.get("hourly_stats", {})
    last_24_hours = sorted(hourly_stats.items(), reverse=True)[:24]
    
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
    
    # Oxirgi 24 soat
    last_24_hours = {}
    for i in range(24):
        hour = (datetime.now() - timedelta(hours=i)).strftime("%H:00")
        last_24_hours[hour] = stats.get("hourly_stats", {}).get(hour, 0)
    
    return jsonify({
        "success": True,
        "data": last_24_hours
    })

@app.route('/api/users')
def api_users():
    """API: Foydalanuvchilar"""
    stats = get_stats()
    return jsonify({
        "success": True,
        "total": len(stats.get("users", [])),
        "users": stats.get("users", [])[:100]  # Faqat birinchi 100 tasi
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

@app.route('/dashboard')
def dashboard():
    """Dashboard sahifasi"""
    return render_template('dashboard.html')

@app.route('/live')
def live_stats():
    """Real-time statistika"""
    return render_template('live.html')

@app.route('/export')
def export_data():
    """Ma'lumotlarni yuklab olish"""
    stats = get_stats()
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "statistics": stats,
        "summary": {
            "total_conversions": stats.get("total_conversions", 0),
            "total_users": len(stats.get("users", [])),
            "total_characters": stats.get("total_characters", 0)
        }
    }
    
    return jsonify(export_data)

# =========== STATIC FILES ===========

@app.route('/static/<path:path>')
def serve_static(path):
    """Static fayllarni server qilish"""
    return send_from_directory('static', path)

# =========== MAIN ===========

if __name__ == '__main__':
    # Data papkasini yaratish
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("📊 Statistika serveri ishga tushmoqda...")
    print("🌐 Dashboard: http://localhost:5001")
    print("📈 API: http://localhost:5001/api/stats")
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)