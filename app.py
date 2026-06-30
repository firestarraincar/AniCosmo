from flask import Flask, send_file, request, jsonify, session
import os
import json
from datetime import datetime, timedelta
import hashlib
import random

app = Flask(__name__)
app.secret_key = 'anicosmo-secret-key-2026'

DATA_FILE = 'wins.json'
USERS_FILE = 'users.json'
SETTINGS_FILE = 'settings.json'
RAFFLES_FILE = 'raffles.json'
COMMENTS_FILE = 'comments.json'
FEEDBACK_FILE = 'feedback.json'
ANNOUNCEMENTS_FILE = 'announcements.json'

# === ЗАГРУЗКА/СОХРАНЕНИЕ ДАННЫХ ===

def load_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {} if file != DATA_FILE else {'wins': [], 'next_id': 1}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    return load_json(DATA_FILE)

def save_data(data):
    save_json(DATA_FILE, data)

def load_users():
    return load_json(USERS_FILE)

def save_users(users):
    save_json(USERS_FILE, users)

def load_settings():
    default = {'code': '132547', 'private_mode': False, 'admin_2fa': False, 'admin_2fa_code': ''}
    data = load_json(SETTINGS_FILE)
    for key in default:
        if key not in data:
            data[key] = default[key]
    return data

def save_settings(settings):
    save_json(SETTINGS_FILE, settings)

def load_raffles():
    return load_json(RAFFLES_FILE)

def save_raffles(raffles):
    save_json(RAFFLES_FILE, raffles)

def load_comments():
    return load_json(COMMENTS_FILE)

def save_comments(comments):
    save_json(COMMENTS_FILE, comments)

def load_feedback():
    return load_json(FEEDBACK_FILE)

def save_feedback(feedback):
    save_json(FEEDBACK_FILE, feedback)

def load_announcements():
    return load_json(ANNOUNCEMENTS_FILE)

def save_announcements(announcements):
    save_json(ANNOUNCEMENTS_FILE, announcements)

# === УТИЛИТЫ ===

def get_user_ip():
    return request.remote_addr

def get_user_level(wins_count):
    if wins_count >= 100:
        return {'name': 'Легенда', 'emoji': '👑', 'color': '#ffd700'}
    elif wins_count >= 50:
        return {'name': 'Профи', 'emoji': '⭐', 'color': '#00bfff'}
    elif wins_count >= 20:
        return {'name': 'Эксперт', 'emoji': '💎', 'color': '#9b59b6'}
    elif wins_count >= 5:
        return {'name': 'Активный', 'emoji': '🔥', 'color': '#ff6b6b'}
    else:
        return {'name': 'Новичок', 'emoji': '🌱', 'color': '#6bcb77'}

def get_user_stats(user):
    data = load_data()
    user_wins = [w for w in data['wins'] if w['user'] == user]
    return {
        'count': len(user_wins),
        'total_value': sum(w['value'] for w in user_wins),
        'wins': user_wins,
        'level': get_user_level(len(user_wins))
    }

def get_top_week():
    data = load_data()
    week_ago = datetime.now() - timedelta(days=7)
    week_wins = [w for w in data['wins'] if datetime.strptime(w['date'], '%d.%m.%Y %H:%M') >= week_ago]
    stats = {}
    for w in week_wins:
        if w['user'] not in stats:
            stats[w['user']] = 0
        stats[w['user']] += 1
    return sorted(stats.items(), key=lambda x: x[1], reverse=True)[:3]

def get_most_valuable_prize():
    data = load_data()
    if not data['wins']:
        return None
    return max(data['wins'], key=lambda w: w['value'])

# === СТРАНИЦА ===

@app.route('/')
def home():
    settings = load_settings()
    if settings.get('private_mode', False) and not session.get('authorized'):
        return login_page()
    return main_page()

def login_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AniCosmo — Вход</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 100vh;
                background-image: url('/background');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }
            .overlay {
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 0, 0, 0.75);
                z-index: 0;
            }
            .login-box {
                position: relative;
                z-index: 1;
                background: rgba(255,255,255,0.06);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 40px 30px;
                width: 100%;
                max-width: 400px;
                border: 1px solid rgba(255,255,255,0.08);
                text-align: center;
            }
            .login-box h1 { font-size: 28px; color: #ff6b6b; margin-bottom: 25px; }
            .login-box input {
                width: 100%;
                padding: 14px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
                background: rgba(255,255,255,0.06);
                color: white;
                font-size: 16px;
                margin-bottom: 15px;
            }
            .login-box input:focus { outline: none; border-color: #ff6b6b; }
            .login-box input::placeholder { color: rgba(255,255,255,0.3); }
            .login-box .btn-login {
                width: 100%; padding: 14px; border: none; border-radius: 10px;
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white; font-size: 18px; font-weight: 600; cursor: pointer;
            }
            .login-box .btn-login:hover { transform: scale(1.02); }
            .login-box .error { color: #ff6b6b; font-size: 14px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="login-box">
            <h1>🔐 AniCosmo</h1>
            <form method="POST" action="/login">
                <input type="text" name="username" placeholder="Логин" required>
                <input type="password" name="password" placeholder="Пароль" required>
                <button type="submit" class="btn-login">Войти</button>
                <div class="error" id="error"></div>
            </form>
        </div>
        <script>
            const params = new URLSearchParams(window.location.search);
            if (params.get('error')) {
                document.getElementById('error').textContent = '❌ ' + params.get('error');
            }
        </script>
    </body>
    </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    users = load_users()
    settings = load_settings()
    
    if username in users and users[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
        # 2FA
        if settings.get('admin_2fa', False) and users[username].get('role') == 'admin':
            session['auth_step'] = '2fa'
            session['username'] = username
            return '''
            <!DOCTYPE html>
            <html><head><meta charset="UTF-8"><title>2FA</title>
            <style>
                *{margin:0;padding:0;box-sizing:border-box}
                body{font-family:'Segoe UI',Arial,sans-serif;min-height:100vh;background-image:url('/background');background-size:cover;background-position:center;color:white;display:flex;justify-content:center;align-items:center;position:relative}
                .overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.75);z-index:0}
                .box{position:relative;z-index:1;background:rgba(255,255,255,0.06);backdrop-filter:blur(10px);border-radius:16px;padding:40px 30px;width:100%;max-width:400px;border:1px solid rgba(255,255,255,0.08);text-align:center}
                .box h1{color:#ff6b6b;margin-bottom:15px}
                .box input{width:100%;padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.06);color:white;font-size:16px;margin-bottom:15px}
                .box input:focus{outline:none;border-color:#ff6b6b}
                .box .btn{width:100%;padding:14px;border:none;border-radius:10px;background:linear-gradient(135deg,#ff6b6b,#ee5a24);color:white;font-size:18px;font-weight:600;cursor:pointer}
                .box .btn:hover{transform:scale(1.02)}
            </style>
            </head>
            <body>
            <div class="overlay"></div>
            <div class="box">
                <h1>🔑 2FA Код</h1>
                <p style="opacity:0.6;margin-bottom:20px;">Введите код подтверждения</p>
                <form method="POST" action="/2fa">
                    <input type="text" name="code" placeholder="Введите код" required>
                    <button type="submit" class="btn">Подтвердить</button>
                </form>
            </div>
            </body>
            </html>
            '''
        session['authorized'] = True
        session['username'] = username
        session['ip'] = get_user_ip()
        return redirect('/')
    
    return redirect('/?error=Неверный логин или пароль')

@app.route('/2fa', methods=['POST'])
def two_factor():
    code = request.form.get('code', '').strip()
    settings = load_settings()
    if code == settings.get('admin_2fa_code', ''):
        session['authorized'] = True
        return redirect('/')
    return redirect('/?error=Неверный 2FA код')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

def redirect(url):
    return f'<meta http-equiv="refresh" content="0;url={url}"><script>window.location.href="{url}"</script>'

# === ОСНОВНАЯ СТРАНИЦА ===

def main_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AniCosmo — Розыгрыши</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 100vh;
                background-image: url('/background');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: white;
                position: relative;
            }
            .overlay {
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 0, 0, 0.7);
                z-index: 0;
            }
            .container {
                position: relative;
                z-index: 1;
                max-width: 1100px;
                margin: 0 auto;
                padding: 40px 20px 100px 20px;
            }

            #screen-main {
                text-align: center;
                padding: 80px 20px;
                transition: opacity 0.8s, transform 0.8s;
            }
            #screen-main h1 {
                font-size: 52px;
                font-weight: 700;
                text-shadow: 0 0 60px rgba(0,0,0,0.8);
                margin-bottom: 25px;
            }
            #screen-main .channel-block { margin-bottom: 45px; }
            #screen-main .channel-block .label {
                font-size: 18px;
                opacity: 0.6;
                letter-spacing: 4px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            #screen-main .channel-block a {
                font-size: 28px;
                color: #ff6b6b;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.3s;
            }
            #screen-main .channel-block a:hover { color: #ff8a8a; }
            .btn {
                padding: 16px 60px;
                font-size: 20px;
                font-weight: 500;
                letter-spacing: 3px;
                color: white;
                background: rgba(255,255,255,0.08);
                border: 2px solid rgba(255,255,255,0.25);
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
                backdrop-filter: blur(4px);
            }
            .btn:hover {
                background: rgba(255,255,255,0.15);
                border-color: rgba(255,255,255,0.5);
                transform: scale(1.03);
            }

            #screen-content {
                display: none;
                opacity: 0;
                transition: opacity 0.8s;
            }
            #screen-content.active {
                display: block;
                opacity: 1;
            }

            .card {
                background: rgba(255,255,255,0.06);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 25px;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .card h3 {
                font-size: 20px;
                font-weight: 500;
                margin-bottom: 15px;
                letter-spacing: 1px;
                color: #ff6b6b;
            }

            .leaderboard-table {
                width: 100%;
                border-collapse: collapse;
            }
            .leaderboard-table th,
            .leaderboard-table td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid rgba(255,255,255,0.06);
            }
            .leaderboard-table th {
                color: rgba(255,255,255,0.5);
                font-weight: 400;
                font-size: 14px;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            .leaderboard-table tr:hover td {
                background: rgba(255,255,255,0.03);
            }
            .leaderboard-table .rank { color: #ffd93d; font-weight: 600; }
            .leaderboard-table .total { color: #6bcb77; font-weight: 600; }

            .win-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                flex-wrap: wrap;
                gap: 8px;
            }
            .win-item:last-child { border-bottom: none; }
            .win-item .win-id { font-size: 11px; color: rgba(255,255,255,0.2); margin-right: 8px; }
            .win-item .win-user { font-weight: 500; }
            .win-item .win-prize { color: #ffd93d; }
            .win-item .win-value { color: #6bcb77; font-weight: 600; }
            .win-item .win-date { font-size: 12px; color: rgba(255,255,255,0.3); }
            .win-item .btn-delete {
                padding: 4px 14px; font-size: 12px;
                color: rgba(255,107,107,0.6);
                background: rgba(255,107,107,0.1);
                border: 1px solid rgba(255,107,107,0.2);
                border-radius: 20px;
                cursor: pointer;
            }
            .win-item .btn-delete:hover { background: rgba(255,107,107,0.2); color: #ff6b6b; }
            .win-item .btn-like {
                padding: 4px 12px; font-size: 13px;
                background: transparent; border: none; color: rgba(255,255,255,0.4);
                cursor: pointer;
            }
            .win-item .btn-like:hover { color: #ff6b6b; }

            .btn-back {
                margin-top: 20px;
                padding: 12px 40px;
                font-size: 16px;
                color: rgba(255,255,255,0.6);
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
            }
            .btn-back:hover { background: rgba(255,255,255,0.1); color: white; }

            .footer { text-align: center; color: rgba(255,255,255,0.12); font-size: 13px; letter-spacing: 3px; padding: 30px 0 10px; }

            .toast {
                padding: 10px 20px; border-radius: 10px; display: none;
                position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
                z-index: 200; max-width: 90%; text-align: center;
            }
            .toast.success { display: block; background: rgba(107,203,119,0.95); color: white; }
            .toast.error { display: block; background: rgba(255,107,107,0.95); color: white; }
            .toast.info { display: block; background: rgba(255,217,61,0.95); color: #1a1a2e; }

            .fab {
                position: fixed; bottom: 30px; right: 30px;
                width: 64px; height: 64px; border-radius: 50%;
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white; border: none; font-size: 32px; cursor: pointer;
                box-shadow: 0 4px 20px rgba(238,90,36,0.4);
                transition: all 0.3s; z-index: 50;
                display: none; align-items: center; justify-content: center;
            }
            .fab:hover { transform: scale(1.1); box-shadow: 0 6px 30px rgba(238,90,36,0.6); }
            .fab.show { display: flex; }

            .modal {
                display: none; position: fixed; top: 0; left: 0;
                width: 100%; height: 100%; background: rgba(0,0,0,0.7);
                z-index: 100; justify-content: center; align-items: center;
            }
            .modal.active { display: flex; }
            .modal-content {
                background: rgba(30,30,50,0.95); backdrop-filter: blur(10px);
                padding: 30px; border-radius: 16px; max-width: 500px; width: 90%;
                border: 1px solid rgba(255,255,255,0.1);
                max-height: 90vh; overflow-y: auto;
            }
            .modal-content h3 { margin-bottom: 15px; color: #ff6b6b; text-align: center; font-size: 24px; }
            .modal-content .form-group { display: flex; flex-direction: column; gap: 12px; margin-bottom: 15px; }
            .modal-content .form-group input, .modal-content .form-group select, .modal-content .form-group textarea {
                padding: 12px 16px; border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
                background: rgba(255,255,255,0.06); color: white; font-size: 15px; width: 100%;
            }
            .modal-content .form-group input:focus, .modal-content .form-group select:focus, .modal-content .form-group textarea:focus {
                outline: none; border-color: #ff6b6b;
            }
            .modal-content .form-group input::placeholder, .modal-content .form-group textarea::placeholder {
                color: rgba(255,255,255,0.4);
            }
            .modal-content .form-group input:disabled { opacity: 0.4; cursor: not-allowed; }
            .modal-content .form-group textarea { resize: vertical; min-height: 60px; font-family: inherit; }
            .modal-buttons {
                display: flex; gap: 12px; justify-content: center; margin-top: 10px;
            }
            .modal-buttons button {
                padding: 10px 30px; border-radius: 10px; border: none; font-size: 15px; cursor: pointer;
            }
            .modal-buttons .btn-submit-modal { background: #ff6b6b; color: white; }
            .modal-buttons .btn-submit-modal:hover:not(:disabled) { background: #ee5a24; }
            .modal-buttons .btn-submit-modal:disabled { opacity: 0.3; cursor: not-allowed; }
            .modal-buttons .btn-cancel { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6); }
            .modal-buttons .btn-cancel:hover { background: rgba(255,255,255,0.15); }
            .modal-content .code-status { text-align: center; font-size: 14px; min-height: 24px; }
            .modal-content .code-status.success { color: #6bcb77; }
            .modal-content .code-status.error { color: #ff6b6b; }

            .level-badge {
                display: inline-block; padding: 2px 12px; border-radius: 20px;
                font-size: 12px; font-weight: 600;
            }

            .raffle-item {
                padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .raffle-item:last-child { border-bottom: none; }
            .raffle-item .raffle-title { font-weight: 600; font-size: 18px; }
            .raffle-item .raffle-status {
                display: inline-block; padding: 2px 12px; border-radius: 20px; font-size: 12px;
            }
            .raffle-item .raffle-status.active { background: rgba(107,203,119,0.3); color: #6bcb77; }
            .raffle-item .raffle-status.ended { background: rgba(255,107,107,0.3); color: #ff6b6b; }
            .raffle-item .raffle-status.planned { background: rgba(255,217,61,0.3); color: #ffd93d; }

            .comment-item {
                padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
                display: flex; gap: 12px;
            }
            .comment-item .comment-user { font-weight: 600; color: #ff6b6b; }
            .comment-item .comment-text { opacity: 0.8; }

            @media (max-width: 600px) {
                #screen-main h1 { font-size: 32px; }
                .fab { width: 56px; height: 56px; font-size: 28px; bottom: 20px; right: 20px; }
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">

            <div id="screen-main">
                <h1>AniCosmo — канал по Аникарду</h1>
                <div class="channel-block">
                    <div class="label">Канал</div>
                    <a href="https://t.me/AniCosmoDay" target="_blank">@AniCosmoDay</a>
                </div>
                <button class="btn" onclick="goForward()">Начать</button>
            </div>

            <div id="screen-content">
                <div style="text-align:center; margin-bottom:30px;">
                    <h2 style="font-size:38px; font-weight:300; letter-spacing:2px;">✨ Добро пожаловать!</h2>
                    <p style="opacity:0.6; margin-top:8px;">Управление розыгрышами AniCosmo</p>
                </div>

                <!-- СТАТИСТИКА -->
                <div class="card" id="statsCard">
                    <h3>📊 Статистика</h3>
                    <div id="statsContent">Загрузка...</div>
                </div>

                <!-- АКТИВНЫЕ РОЗЫГРЫШИ -->
                <div class="card" id="activeRafflesCard">
                    <h3>🎯 Активные розыгрыши</h3>
                    <div id="activeRaffles">Загрузка...</div>
                </div>

                <!-- АРХИВ РОЗЫГРЫШЕЙ -->
                <div class="card" id="archivedRafflesCard">
                    <h3>📦 Архив розыгрышей</h3>
                    <div id="archivedRaffles">Загрузка...</div>
                </div>

                <div class="card">
                    <h3>🏆 Лидерборд</h3>
                    <div id="leaderboard">Загрузка...</div>
                </div>

                <div class="card">
                    <h3>📋 Недавние выигрыши</h3>
                    <div id="recentWins">Загрузка...</div>
                </div>

                <!-- ТОП НЕДЕЛИ -->
                <div class="card" id="topWeekCard">
                    <h3>🔥 Топ-3 недели</h3>
                    <div id="topWeek">Загрузка...</div>
                </div>

                <!-- САМЫЙ ДОРОГОЙ ПРИЗ -->
                <div class="card" id="mostValuableCard">
                    <h3>💎 Самый дорогой приз</h3>
                    <div id="mostValuable">Загрузка...</div>
                </div>

                <!-- АНОНСЫ -->
                <div class="card" id="announcementsCard">
                    <h3>📢 Анонсы</h3>
                    <div id="announcements">Загрузка...</div>
                </div>

                <!-- ОТЗЫВЫ -->
                <div class="card" id="feedbackCard">
                    <h3>💬 Отзывы</h3>
                    <div id="feedbackList">Загрузка...</div>
                </div>

                <div style="text-align:center;">
                    <button class="btn-back" onclick="goBack()">← Назад</button>
                </div>
            </div>

            <div class="footer">ANICOSMO</div>
        </div>

        <button class="fab" id="fab" onclick="openMainMenu()">+</button>

        <!-- ГЛАВНОЕ МЕНЮ -->
        <div class="modal" id="mainMenu">
            <div class="modal-content">
                <h3>📋 Меню</h3>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <button onclick="closeModal('mainMenu');openAddModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">➕ Добавить выигрыш</button>
                    <button onclick="closeModal('mainMenu');openRaffleModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">🎲 Создать розыгрыш</button>
                    <button onclick="closeModal('mainMenu');openRandomModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">🎰 Случайный выбор</button>
                    <button onclick="closeModal('mainMenu');openWheelModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">🎡 Колесо фортуны</button>
                    <button onclick="closeModal('mainMenu');openAnnouncementModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">📢 Создать анонс</button>
                    <button onclick="closeModal('mainMenu');openFeedbackModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">💬 Оставить отзыв</button>
                    <button onclick="closeModal('mainMenu');openUserProfileModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">👤 Профиль участника</button>
                    <button onclick="closeModal('mainMenu');openSettingsModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">⚙️ Настройки</button>
                    <button onclick="closeModal('mainMenu');" style="padding:12px;border-radius:10px;background:rgba(255,107,107,0.2);border:1px solid rgba(255,107,107,0.3);color:#ff6b6b;font-size:16px;cursor:pointer;">❌ Закрыть</button>
                </div>
            </div>
        </div>

        <!-- МОДАЛКА ДОБАВЛЕНИЯ ВЫИГРЫША -->
        <div class="modal" id="addModal">
            <div class="modal-content">
                <h3>➕ Добавить выигрыш</h3>
                <div class="form-group">
                    <input type="password" id="modalCode" placeholder="Введите код" oninput="checkCode()">
                    <div class="code-status" id="codeStatus"></div>
                </div>
                <div class="form-group">
                    <input type="text" id="modalUser" placeholder="Имя участника или @telegram" disabled>
                    <input type="text" id="modalPrize" placeholder="Что выиграл" disabled>
                    <input type="number" id="modalValue" placeholder="Ценность в ПТ" disabled>
                    <input type="text" id="modalComment" placeholder="Комментарий к выигрышу (опционально)" disabled>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('addModal')">Отмена</button>
                    <button class="btn-submit-modal" id="modalSubmitBtn" onclick="submitWin()" disabled>Опубликовать</button>
                </div>
            </div>
        </div>

        <!-- МОДАЛКА УДАЛЕНИЯ -->
        <div class="modal" id="deleteModal">
            <div class="modal-content">
                <h3>🗑️ Удалить выигрыш?</h3>
                <p style="opacity:0.6; margin-bottom:15px; text-align:center;">Введите код для подтверждения</p>
                <input type="password" id="deleteCodeInput" placeholder="Введите код" style="width:100%; padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.15); background:rgba(255,255,255,0.06); color:white; font-size:16px; margin-bottom:15px; text-align:center;">
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('deleteModal')">Отмена</button>
                    <button class="btn-submit-modal" onclick="confirmDelete()" style="background:#ff6b6b; color:white;">Удалить</button>
                </div>
            </div>
        </div>

        <!-- МОДАЛКА РОЗЫГРЫША -->
        <div class="modal" id="raffleModal">
            <div class="modal-content">
                <h3>🎲 Создать розыгрыш</h3>
                <div class="form-group">
                    <input type="password" id="raffleCode" placeholder="Введите код" oninput="checkRaffleCode()">
                    <div class="code-status" id="raffleCodeStatus"></div>
                </div>
                <div class="form-group">
                    <input type="text" id="raffleTitle" placeholder="Название розыгрыша" disabled>
                    <input type="text" id="rafflePrize" placeholder="Приз" disabled>
                    <input type="number" id="raffleValue" placeholder="Ценность в ПТ" disabled>
                    <input type="datetime-local" id="raffleTime" disabled>
                    <select id="raffleType" disabled>
                        <option value="standard">Стандартный</option>
                        <option value="random">Случайный победитель</option>
                        <option value="wheel">Колесо фортуны</option>
                    </select>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('raffleModal')">Отмена</button>
                    <button class="btn-submit-modal" id="raffleSubmitBtn" onclick="submitRaffle()" disabled>Создать</button>
                </div>
            </div>
        </div>

        <!-- МОДАЛКА СЛУЧАЙНОГО ВЫБОРА -->
        <div class="modal" id="randomModal">
            <div class="modal-content">
                <h3>🎰 Случайный выбор</h3>
                <p style="opacity:0.6;margin-bottom:15px;">Выберите участников через запятую</p>
                <div class="form-group">
                    <input type="password" id="randomCode" placeholder="Введите код" oninput="checkRandomCode()">
                    <div class="code-status" id="randomCodeStatus"></div>
                </div>
                <div class="form-group">
                    <textarea id="randomUsers" placeholder="Участники через запятую" disabled></textarea>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('randomModal')">Отмена</button>
                    <button class="btn-submit-modal" id="randomSubmitBtn" onclick="randomPick()" disabled>Выбрать</button>
                </div>
                <div id="randomResult" style="text-align:center;margin-top:15px;font-size:20px;"></div>
            </div>
        </div>

        <!-- МОДАЛКА КОЛЕСА -->
        <div class="modal" id="wheelModal">
            <div class="modal-content">
                <h3>🎡 Колесо фортуны</h3>
                <p style="opacity:0.6;margin-bottom:15px;">Введите участников через запятую</p>
                <div class="form-group">
                    <input type="password" id="wheelCode" placeholder="Введите код" oninput="checkWheelCode()">
                    <div class="code-status" id="wheelCodeStatus"></div>
                </div>
                <div class="form-group">
                    <textarea id="wheelUsers" placeholder="Участники через запятую" disabled></textarea>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('wheelModal')">Отмена</button>
                    <button class="btn-submit-modal" id="wheelSubmitBtn" onclick="spinWheel()" disabled>Крутить</button>
                </div>
                <div id="wheelResult" style="text-align:center;margin-top:15px;font-size:28px;"></div>
            </div>
        </div>

        <!-- МОДАЛКА АНОНСА -->
        <div class="modal" id="announcementModal">
            <div class="modal-content">
                <h3>📢 Создать анонс</h3>
                <div class="form-group">
                    <input type="password" id="annCode" placeholder="Введите код" oninput="checkAnnCode()">
                    <div class="code-status" id="annCodeStatus"></div>
                </div>
                <div class="form-group">
                    <input type="text" id="annTitle" placeholder="Заголовок" disabled>
                    <textarea id="annText" placeholder="Текст анонса" disabled></textarea>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('announcementModal')">Отмена</button>
                    <button class="btn-submit-modal" id="annSubmitBtn" onclick="submitAnnouncement()" disabled>Опубликовать</button>
                </div>
            </div>
        </div>

        <!-- МОДАЛКА ОТЗЫВА -->
        <div class="modal" id="feedbackModal">
            <div class="modal-content">
                <h3>💬 Оставить отзыв</h3>
                <div class="form-group">
                    <input type="text" id="fbUser" placeholder="Ваше имя">
                    <textarea id="fbText" placeholder="Ваш отзыв"></textarea>
                    <input type="number" id="fbRating" placeholder="Оценка (1-5)" min="1" max="5">
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('feedbackModal')">Отмена</button>
                    <button class="btn-submit-modal" onclick="submitFeedback()">Отправить</button>
                </div>
            </div>
        </div>

        <!-- МОДАЛКА ПРОФИЛЯ -->
        <div class="modal" id="profileModal">
            <div class="modal-content">
                <h3>👤 Профиль участника</h3>
                <div class="form-group">
                    <input type="text" id="profileUser" placeholder="Имя участника">
                    <button class="btn-submit-modal" onclick="loadProfile()" style="padding:10px;">Показать</button>
                </div>
                <div id="profileResult" style="margin-top:15px;"></div>
            </div>
        </div>

        <!-- МОДАЛКА НАСТРОЕК -->
        <div class="modal" id="settingsModal">
            <div class="modal-content">
                <h3>⚙️ Настройки</h3>
                <div class="form-group">
                    <input type="password" id="settingsCode" placeholder="Введите текущий код" oninput="checkSettingsCode()">
                    <div class="code-status" id="settingsCodeStatus"></div>
                </div>
                <div class="form-group">
                    <input type="text" id="settingsNewCode" placeholder="Новый код" disabled>
                    <button class="btn-submit-modal" id="settingsChangeBtn" onclick="changeCode()" disabled>Сменить код</button>
                </div>
                <div style="margin-top:15px;border-top:1px solid rgba(255,255,255,0.1);padding-top:15px;">
                    <label><input type="checkbox" id="privateMode"> Приватный режим</label>
                </div>
                <div style="margin-top:10px;">
                    <label><input type="checkbox" id="admin2fa"> 2FA для админа</label>
                </div>
                <div class="form-group" id="faCodeGroup" style="display:none;">
                    <input type="text" id="settings2faCode" placeholder="2FA код">
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('settingsModal')">Закрыть</button>
                </div>
            </div>
        </div>

        <script>
            let deleteTargetId = null;
            let codeVerified = false;
            let raffleCodeVerified = false;
            let randomCodeVerified = false;
            let wheelCodeVerified = false;
            let annCodeVerified = false;
            let settingsCodeVerified = false;

            // === ПЕРЕХОДЫ ===
            function goForward() {
                const main = document.getElementById('screen-main');
                main.style.opacity = '0';
                main.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    main.style.display = 'none';
                    const content = document.getElementById('screen-content');
                    content.style.display = 'block';
                    setTimeout(() => {
                        content.classList.add('active');
                        document.getElementById('fab').classList.add('show');
                    }, 50);
                    loadData();
                }, 500);
            }

            function goBack() {
                const content = document.getElementById('screen-content');
                content.classList.remove('active');
                document.getElementById('fab').classList.remove('show');
                setTimeout(() => {
                    content.style.display = 'none';
                    const main = document.getElementById('screen-main');
                    main.style.display = 'block';
                    setTimeout(() => {
                        main.style.opacity = '1';
                        main.style.transform = 'scale(1)';
                    }, 50);
                }, 400);
            }

            // === МОДАЛКИ ===
            function openModal(id) { document.getElementById(id).classList.add('active'); }
            function closeModal(id) { document.getElementById(id).classList.remove('active'); }

            function openMainMenu() { openModal('mainMenu'); }
            function openAddModal() { openModal('addModal'); document.getElementById('modalCode').focus(); }
            function openRaffleModal() { openModal('raffleModal'); document.getElementById('raffleCode').focus(); }
            function openRandomModal() { openModal('randomModal'); document.getElementById('randomCode').focus(); }
            function openWheelModal() { openModal('wheelModal'); document.getElementById('wheelCode').focus(); }
            function openAnnouncementModal() { openModal('announcementModal'); document.getElementById('annCode').focus(); }
            function openFeedbackModal() { openModal('feedbackModal'); }
            function openUserProfileModal() { openModal('profileModal'); }
            function openSettingsModal() { 
                openModal('settingsModal'); 
                document.getElementById('settingsCode').focus();
                fetch('/api/settings')
                    .then(r => r.json())
                    .then(d => {
                        document.getElementById('privateMode').checked = d.private_mode || false;
                        document.getElementById('admin2fa').checked = d.admin_2fa || false;
                        document.getElementById('faCodeGroup').style.display = d.admin_2fa ? 'block' : 'none';
                    });
            }

            // === ТОСТЫ ===
            function showToast(message, type = 'info') {
                const toast = document.createElement('div');
                toast.className = 'toast ' + type;
                toast.textContent = message;
                document.body.appendChild(toast);
                setTimeout(() => { toast.remove(); }, 4000);
            }

            // === ЗАГРУЗКА ДАННЫХ ===
            async function loadData() {
                try {
                    const res = await fetch('/api/wins');
                    const data = await res.json();
                    renderWins(data.wins);
                    renderLeaderboard(data.wins);
                    renderStats(data.wins);
                    renderTopWeek(data.wins);
                    renderMostValuable(data.wins);
                    await loadRaffles();
                    await loadAnnouncements();
                    await loadFeedback();
                } catch (e) { console.error(e); }
            }

            function renderWins(wins) {
                const container = document.getElementById('recentWins');
                if (!wins || wins.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4;text-align:center;padding:20px;">Пока нет выигрышей</div>';
                    return;
                }
                const sorted = [...wins].reverse().slice(0, 20);
                container.innerHTML = sorted.map(w => `
                    <div class="win-item">
                        <div>
                            <span class="win-id">#${w.id}</span>
                            <span class="win-user">${w.user}</span>
                            ${w.comment ? `<span style="font-size:12px;opacity:0.4;margin-left:8px;">💬 ${w.comment}</span>` : ''}
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                            <span class="win-prize">${w.prize}</span>
                            <span class="win-value">${w.value} ПТ</span>
                            <span class="win-date">${w.date}</span>
                            <button class="btn-like" onclick="likeWin(${w.id})">❤️ ${w.likes || 0}</button>
                            <button class="btn-delete" onclick="openDeleteModal(${w.id})">✕</button>
                        </div>
                    </div>
                `).join('');
            }

            function renderLeaderboard(wins) {
                const container = document.getElementById('leaderboard');
                if (!wins || wins.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4;text-align:center;padding:20px;">Нет данных</div>';
                    return;
                }
                const stats = {};
                wins.forEach(w => {
                    if (!stats[w.user]) stats[w.user] = { total: 0, count: 0 };
                    stats[w.user].total += w.value;
                    stats[w.user].count += 1;
                });
                const sorted = Object.entries(stats).sort((a,b) => b[1].total - a[1].total).slice(0, 10);
                let html = `<table class="leaderboard-table"><tr><th>#</th><th>Участник</th><th>Кол-во</th><th>Сумма ПТ</th><th>Уровень</th></tr>`;
                sorted.forEach(([user, data], i) => {
                    const rank = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i+1}`;
                    const level = getLevel(data.count);
                    html += `<tr>
                        <td class="rank">${rank}</td>
                        <td><strong>${user}</strong></td>
                        <td>${data.count} раз</td>
                        <td class="total">${data.total} ПТ</td>
                        <td><span class="level-badge" style="background:${level.color}20;color:${level.color};border:1px solid ${level.color}40;">${level.emoji} ${level.name}</span></td>
                    </tr>`;
                });
                html += '</table>';
                container.innerHTML = html;
            }

            function renderStats(wins) {
                const container = document.getElementById('statsContent');
                if (!wins || wins.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4;text-align:center;">Нет данных</div>';
                    return;
                }
                const users = new Set(wins.map(w => w.user));
                const totalValue = wins.reduce((s, w) => s + w.value, 0);
                const avg = (totalValue / wins.length).toFixed(1);
                container.innerHTML = `
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:15px;text-align:center;">
                        <div><div style="font-size:28px;font-weight:700;color:#ff6b6b;">${wins.length}</div><div style="opacity:0.5;font-size:13px;">Всего выигрышей</div></div>
                        <div><div style="font-size:28px;font-weight:700;color:#6bcb77;">${users.size}</div><div style="opacity:0.5;font-size:13px;">Участников</div></div>
                        <div><div style="font-size:28px;font-weight:700;color:#ffd93d;">${totalValue}</div><div style="opacity:0.5;font-size:13px;">Всего ПТ</div></div>
                        <div><div style="font-size:28px;font-weight:700;color:#00bfff;">${avg}</div><div style="opacity:0.5;font-size:13px;">Средняя ценность</div></div>
                    </div>
                `;
            }

            function renderTopWeek(wins) {
                const container = document.getElementById('topWeek');
                const weekAgo = new Date(Date.now() - 7*24*60*60*1000);
                const weekWins = wins.filter(w => new Date(w.date.split(' ')[0].split('.').reverse().join('-') + 'T' + w.date.split(' ')[1]) >= weekAgo);
                const stats = {};
                weekWins.forEach(w => { stats[w.user] = (stats[w.user] || 0) + 1; });
                const sorted = Object.entries(stats).sort((a,b) => b[1] - a[1]).slice(0, 3);
                if (sorted.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4;text-align:center;">Нет данных за неделю</div>';
                    return;
                }
                const emojis = ['🥇', '🥈', '🥉'];
                container.innerHTML = sorted.map(([user, count], i) => 
                    `<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">${emojis[i] || '•'} <strong>${user}</strong> — ${count} выигрышей</div>`
                ).join('');
            }

            function renderMostValuable(wins) {
                const container = document.getElementById('mostValuable');
                if (!wins || wins.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4;text-align:center;">Нет данных</div>';
                    return;
                }
                const best = wins.reduce((a,b) => a.value > b.value ? a : b);
                container.innerHTML = `
                    <div style="padding:10px;background:rgba(255,215,0,0.05);border-radius:10px;border:1px solid rgba(255,215,0,0.1);">
                        🎁 <strong>${best.prize}</strong> — ${best.user} (${best.value} ПТ) 📅 ${best.date}
                        ${best.comment ? `<br><span style="opacity:0.5;font-size:14px;">💬 ${best.comment}</span>` : ''}
                    </div>
                `;
            }

            function getLevel(count) {
                if (count >= 100) return {name:'Легенда', emoji:'👑', color:'#ffd700'};
                if (count >= 50) return {name:'Профи', emoji:'⭐', color:'#00bfff'};
                if (count >= 20) return {name:'Эксперт', emoji:'💎', color:'#9b59b6'};
                if (count >= 5) return {name:'Активный', emoji:'🔥', color:'#ff6b6b'};
                return {name:'Новичок', emoji:'🌱', color:'#6bcb77'};
            }

            // === РОЗЫГРЫШИ ===
            async function loadRaffles() {
                try {
                    const res = await fetch('/api/raffles');
                    const data = await res.json();
                    const active = data.filter(r => r.status === 'active');
                    const archived = data.filter(r => r.status === 'ended' || r.status === 'planned');
                    document.getElementById('activeRaffles').innerHTML = active.length ? active.map(r => `
                        <div class="raffle-item">
                            <div class="raffle-title">${r.title}</div>
                            <div>🎁 ${r.prize} — ${r.value} ПТ</div>
                            <div><span class="raffle-status active">Активен</span> до ${r.end_time || 'не указано'}</div>
                            <button onclick="joinRaffle(${r.id})" style="padding:4px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:white;cursor:pointer;margin-top:5px;">Участвовать</button>
                        </div>
                    `).join('') : '<div style="opacity:0.4;text-align:center;padding:10px;">Нет активных розыгрышей</div>';
                    document.getElementById('archivedRaffles').innerHTML = archived.length ? archived.map(r => `
                        <div class="raffle-item">
                            <div class="raffle-title">${r.title}</div>
                            <div>🎁 ${r.prize} — ${r.value} ПТ</div>
                            <div><span class="raffle-status ${r.status === 'ended' ? 'ended' : 'planned'}">${r.status === 'ended' ? 'Завершён' : 'Запланирован'}</span></div>
                            <div style="font-size:12px;opacity:0.4;">Участников: ${(r.participants || []).length}</div>
                        </div>
                    `).join('') : '<div style="opacity:0.4;text-align:center;padding:10px;">Нет завершённых розыгрышей</div>';
                } catch(e) { console.error(e); }
            }

            function checkRaffleCode() {
                const code = document.getElementById('raffleCode').value.trim();
                const status = document.getElementById('raffleCodeStatus');
                const correct = '132547';
                if (code === correct) {
                    status.textContent = '✅ Код верный!';
                    status.className = 'code-status success';
                    document.querySelectorAll('#raffleModal .form-group input, #raffleModal .form-group select').forEach(el => el.disabled = false);
                    document.getElementById('raffleSubmitBtn').disabled = false;
                    raffleCodeVerified = true;
                } else if (code.length > 0) {
                    status.textContent = '❌ Неверный код';
                    status.className = 'code-status error';
                    document.querySelectorAll('#raffleModal .form-group input, #raffleModal .form-group select').forEach(el => el.disabled = true);
                    document.getElementById('raffleSubmitBtn').disabled = true;
                    raffleCodeVerified = false;
                } else {
                    status.textContent = '';
                    status.className = 'code-status';
                    document.querySelectorAll('#raffleModal .form-group input, #raffleModal .form-group select').forEach(el => el.disabled = true);
                    document.getElementById('raffleSubmitBtn').disabled = true;
                    raffleCodeVerified = false;
                }
            }

            async function submitRaffle() {
                if (!raffleCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                const title = document.getElementById('raffleTitle').value.trim();
                const prize = document.getElementById('rafflePrize').value.trim();
                const value = parseInt(document.getElementById('raffleValue').value);
                const time = document.getElementById('raffleTime').value;
                const type = document.getElementById('raffleType').value;
                if (!title || !prize || !value) { showToast('❌ Заполните все поля!', 'error'); return; }
                try {
                    const res = await fetch('/api/raffle', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, prize, value, end_time: time, type })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('✅ Розыгрыш создан!', 'success');
                        closeModal('raffleModal');
                        loadData();
                    } else { showToast('❌ ' + result.error, 'error'); }
                } catch(e) { showToast('❌ Ошибка сервера', 'error'); }
            }

            async function joinRaffle(id) {
                const user = prompt('Введите ваше имя или @telegram:');
                if (!user) return;
                try {
                    const res = await fetch('/api/raffle/join', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id, user })
                    });
                    const result = await res.json();
                    if (result.success) { showToast('✅ Вы участвуете!', 'success'); loadData(); }
                    else { showToast('❌ ' + result.error, 'error'); }
                } catch(e) { showToast('❌ Ошибка', 'error'); }
            }

            // === СЛУЧАЙНЫЙ ВЫБОР ===
            function checkRandomCode() {
                const code = document.getElementById('randomCode').value.trim();
                const status = document.getElementById('randomCodeStatus');
                if (code === '132547') {
                    status.textContent = '✅ Код верный!'; status.className = 'code-status success';
                    document.getElementById('randomUsers').disabled = false;
                    document.getElementById('randomSubmitBtn').disabled = false;
                    randomCodeVerified = true;
                } else if (code.length > 0) {
                    status.textContent = '❌ Неверный код'; status.className = 'code-status error';
                    document.getElementById('randomUsers').disabled = true;
                    document.getElementById('randomSubmitBtn').disabled = true;
                    randomCodeVerified = false;
                } else {
                    status.textContent = ''; status.className = 'code-status';
                    document.getElementById('randomUsers').disabled = true;
                    document.getElementById('randomSubmitBtn').disabled = true;
                    randomCodeVerified = false;
                }
            }

            function randomPick() {
                if (!randomCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                const users = document.getElementById('randomUsers').value.split(',').map(s => s.trim()).filter(s => s);
                if (users.length === 0) { showToast('❌ Введите участников!', 'error'); return; }
                const winner = users[Math.floor(Math.random() * users.length)];
                document.getElementById('randomResult').innerHTML = `🎉 Победитель: <strong style="color:#ffd93d;font-size:32px;">${winner}</strong> 🎉`;
            }

            // === КОЛЕСО ФОРТУНЫ ===
            function checkWheelCode() {
                const code = document.getElementById('wheelCode').value.trim();
                const status = document.getElementById('wheelCodeStatus');
                if (code === '132547') {
                    status.textContent = '✅ Код верный!'; status.className = 'code-status success';
                    document.getElementById('wheelUsers').disabled = false;
                    document.getElementById('wheelSubmitBtn').disabled = false;
                    wheelCodeVerified = true;
                } else if (code.length > 0) {
                    status.textContent = '❌ Неверный код'; status.className = 'code-status error';
                    document.getElementById('wheelUsers').disabled = true;
                    document.getElementById('wheelSubmitBtn').disabled = true;
                    wheelCodeVerified = false;
                } else {
                    status.textContent = ''; status.className = 'code-status';
                    document.getElementById('wheelUsers').disabled = true;
                    document.getElementById('wheelSubmitBtn').disabled = true;
                    wheelCodeVerified = false;
                }
            }

            function spinWheel() {
                if (!wheelCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                const users = document.getElementById('wheelUsers').value.split(',').map(s => s.trim()).filter(s => s);
                if (users.length === 0) { showToast('❌ Введите участников!', 'error'); return; }
                let spins = 0;
                const interval = setInterval(() => {
                    const randomUser = users[Math.floor(Math.random() * users.length)];
                    document.getElementById('wheelResult').textContent = `🎡 ${randomUser}`;
                    spins++;
                    if (spins > 20) {
                        clearInterval(interval);
                        const winner = users[Math.floor(Math.random() * users.length)];
                        document.getElementById('wheelResult').innerHTML = `🎉 Победитель: <strong style="color:#ffd93d;font-size:32px;">${winner}</strong> 🎉`;
                        showToast(`🎉 Победитель: ${winner}`, 'success');
                    }
                }, 100);
            }

            // === АНОНСЫ ===
            function checkAnnCode() {
                const code = document.getElementById('annCode').value.trim();
                const status = document.getElementById('annCodeStatus');
                if (code === '132547') {
                    status.textContent = '✅ Код верный!'; status.className = 'code-status success';
                    document.getElementById('annTitle').disabled = false;
                    document.getElementById('annText').disabled = false;
                    document.getElementById('annSubmitBtn').disabled = false;
                    annCodeVerified = true;
                } else if (code.length > 0) {
                    status.textContent = '❌ Неверный код'; status.className = 'code-status error';
                    document.getElementById('annTitle').disabled = true;
                    document.getElementById('annText').disabled = true;
                    document.getElementById('annSubmitBtn').disabled = true;
                    annCodeVerified = false;
                } else {
                    status.textContent = ''; status.className = 'code-status';
                    document.getElementById('annTitle').disabled = true;
                    document.getElementById('annText').disabled = true;
                    document.getElementById('annSubmitBtn').disabled = true;
                    annCodeVerified = false;
                }
            }

            async function submitAnnouncement() {
                if (!annCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                const title = document.getElementById('annTitle').value.trim();
                const text = document.getElementById('annText').value.trim();
                if (!title || !text) { showToast('❌ Заполните все поля!', 'error'); return; }
                try {
                    const res = await fetch('/api/announcement', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, text })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('✅ Анонс опубликован!', 'success');
                        closeModal('announcementModal');
                        loadData();
                    } else { showToast('❌ ' + result.error, 'error'); }
                } catch(e) { showToast('❌ Ошибка', 'error'); }
            }

            async function loadAnnouncements() {
                try {
                    const res = await fetch('/api/announcements');
                    const data = await res.json();
                    document.getElementById('announcements').innerHTML = data.length ? data.map(a => `
                        <div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                            <div style="font-weight:600;">${a.title}</div>
                            <div style="opacity:0.7;font-size:14px;">${a.text}</div>
                            <div style="font-size:11px;opacity:0.3;">${a.date}</div>
                        </div>
                    `).join('') : '<div style="opacity:0.4;text-align:center;padding:10px;">Нет анонсов</div>';
                } catch(e) { console.error(e); }
            }

            // === ОТЗЫВЫ ===
            async function submitFeedback() {
                const user = document.getElementById('fbUser').value.trim() || 'Аноним';
                const text = document.getElementById('fbText').value.trim();
                const rating = parseInt(document.getElementById('fbRating').value);
                if (!text) { showToast('❌ Напишите отзыв!', 'error'); return; }
                if (rating < 1 || rating > 5) { showToast('❌ Оценка от 1 до 5', 'error'); return; }
                try {
                    const res = await fetch('/api/feedback', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user, text, rating })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('✅ Спасибо за отзыв!', 'success');
                        closeModal('feedbackModal');
                        loadData();
                        document.getElementById('fbUser').value = '';
                        document.getElementById('fbText').value = '';
                        document.getElementById('fbRating').value = '';
                    } else { showToast('❌ ' + result.error, 'error'); }
                } catch(e) { showToast('❌ Ошибка', 'error'); }
            }

            async function loadFeedback() {
                try {
                    const res = await fetch('/api/feedback');
                    const data = await res.json();
                    document.getElementById('feedbackList').innerHTML = data.length ? data.map(f => `
                        <div class="comment-item">
                            <div>
                                <span class="comment-user">${f.user}</span>
                                <span style="font-size:12px;opacity:0.5;">⭐ ${f.rating}</span>
                                <div class="comment-text">${f.text}</div>
                            </div>
                        </div>
                    `).join('') : '<div style="opacity:0.4;text-align:center;padding:10px;">Нет отзывов</div>';
                } catch(e) { console.error(e); }
            }

            // === ПРОФИЛЬ ===
            async function loadProfile() {
                const user = document.getElementById('profileUser').value.trim();
                if (!user) { showToast('❌ Введите имя участника', 'error'); return; }
                try {
                    const res = await fetch(`/api/user/${encodeURIComponent(user)}`);
                    const data = await res.json();
                    if (!data.found) { document.getElementById('profileResult').innerHTML = '<div style="opacity:0.4;text-align:center;">Участник не найден</div>'; return; }
                    const level = getLevel(data.count);
                    document.getElementById('profileResult').innerHTML = `
                        <div style="padding:15px;background:rgba(255,255,255,0.03);border-radius:10px;">
                            <div style="font-size:24px;font-weight:600;">${user}</div>
                            <div><span class="level-badge" style="background:${level.color}20;color:${level.color};border:1px solid ${level.color}40;">${level.emoji} ${level.name}</span></div>
                            <div style="margin-top:10px;">🏆 Выигрышей: <strong>${data.count}</strong></div>
                            <div>💰 Сумма ПТ: <strong>${data.total_value}</strong></div>
                            <div style="margin-top:10px;font-size:13px;opacity:0.5;">📅 Последние выигрыши:</div>
                            ${data.wins.slice(0,5).map(w => `<div style="font-size:13px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.03);">${w.prize} — ${w.value} ПТ (${w.date})</div>`).join('')}
                        </div>
                    `;
                } catch(e) { showToast('❌ Ошибка', 'error'); }
            }

            // === ЛАЙКИ ===
            async function likeWin(id) {
                try {
                    const res = await fetch('/api/like', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id })
                    });
                    const result = await res.json();
                    if (result.success) { loadData(); }
                } catch(e) { console.error(e); }
            }

            // === УДАЛЕНИЕ ===
            function openDeleteModal(id) {
                deleteTargetId = id;
                openModal('deleteModal');
                document.getElementById('deleteCodeInput').value = '';
                document.getElementById('deleteCodeInput').focus();
            }

            async function confirmDelete() {
                const code = document.getElementById('deleteCodeInput').value.trim();
                if (code !== '132547') { showToast('❌ Неверный код!', 'error'); return; }
                if (deleteTargetId === null) return;
                try {
                    const res = await fetch('/api/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: deleteTargetId })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('✅ Выигрыш удалён!', 'success');
                        closeModal('deleteModal');
                        loadData();
                    } else { showToast('❌ ' + result.error, 'error'); }
                } catch(e) { showToast('❌ Ошибка', 'error'); }
            }

            // === КОД ДЛЯ ДОБАВЛЕНИЯ ===
            function checkCode() {
                const code = document.getElementById('modalCode').value.trim();
                const status = document.getElementById('codeStatus');
                if (code === '132547') {
                    status.textContent = '✅ Код верный!'; status.className = 'code-status success';
                    document.querySelectorAll('#addModal .form-group input').forEach(el => el.disabled = false);
                    document.getElementById('modalSubmitBtn').disabled = false;
                    codeVerified = true;
                } else if (code.length > 0) {
                    status.textContent = '❌ Неверный код'; status.className = 'code-status error';
                    document.querySelectorAll('#addModal .form-group input').forEach(el => el.disabled = true);
                    document.getElementById('modalSubmitBtn').disabled = true;
                    codeVerified = false;
                } else {
                    status.textContent = ''; status.className = 'code-status';
                    document.querySelectorAll('#addModal .form-group input').forEach(el => el.disabled = true);
                    document.getElementById('modalSubmitBtn').disabled = true;
                    codeVerified = false;
                }
            }

            async function submitWin() {
                if (!codeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                const user = document.getElementById('modalUser').value.trim();
                const prize = document.getElementById('modalPrize').value.trim();
                const value = parseInt(document.getElementById('modalValue').value);
                const comment = document.getElementById('modalComment').value.trim();
                if (!user || !prize || !value) { showToast('❌ Заполните все поля!', 'error'); return; }
                if (value <= 0) { showToast('❌ Ценность > 0!', 'error'); return; }
                try {
                    const res = await fetch('/api/add', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user, prize, value, comment })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('✅ Выигрыш добавлен! 🎉', 'success');
                        closeModal('addModal');
                        // АНИМАЦИЯ КОНФЕТТИ
                        confetti();
                        loadData();
                    } else { showToast('❌ ' + result.error, 'error'); }
                } catch(e) { showToast('❌ Ошибка', 'error'); }
            }

            // === КОНФЕТТИ ===
            function confetti() {
                const colors = ['#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#ff6bff'];
                for (let i = 0; i < 80; i++) {
                    const el = document.createElement('div');
                    el.style.cssText = `
                        position:fixed; left:${Math.random()*100}vw; top:-10px;
                        width:${6+Math.random()*8}px; height:${6+Math.random()*8}px;
                        background:${colors[Math.floor(Math.random()*colors.length)]};
                        border-radius:${Math.random()>0.5?'50%':'2px'};
                        z-index:9999; pointer-events:none;
                        transition: all ${1.5+Math.random()*2}s cubic-bezier(0.25,0.1,0.25,1);
                        transform: rotate(${Math.random()*360}deg);
                    `;
                    document.body.appendChild(el);
                    setTimeout(() => {
                        el.style.top = `${80+Math.random()*20}vh`;
                        el.style.left = `${Math.random()*100}vw`;
                        el.style.opacity = '0';
                    }, 10);
                    setTimeout(() => el.remove(), 3500);
                }
            }

            // === НАСТРОЙКИ ===
            function checkSettingsCode() {
                const code = document.getElementById('settingsCode').value.trim();
                const status = document.getElementById('settingsCodeStatus');
                if (code === '132547') {
                    status.textContent = '✅ Код верный!'; status.className = 'code-status success';
                    document.getElementById('settingsNewCode').disabled = false;
                    document.getElementById('settingsChangeBtn').disabled = false;
                    settingsCodeVerified = true;
                } else if (code.length > 0) {
                    status.textContent = '❌ Неверный код'; status.className = 'code-status error';
                    document.getElementById('settingsNewCode').disabled = true;
                    document.getElementById('settingsChangeBtn').disabled = true;
                    settingsCodeVerified = false;
                } else {
                    status.textContent = ''; status.className = 'code-status';
                    document.getElementById('settingsNewCode').disabled = true;
                    document.getElementById('settingsChangeBtn').disabled = true;
                    settingsCodeVerified = false;
                }
            }

            async function changeCode() {
                if (!settingsCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                const newCode = document.getElementById('settingsNewCode').value.trim();
                if (!newCode || newCode.length < 4) { showToast('❌ Код должен быть минимум 4 символа', 'error'); return; }
                try {
                    const res = await fetch('/api/settings/code', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ new_code: newCode })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('✅ Код изменён!', 'success');
                        closeModal('settingsModal');
                    } else { showToast('❌ ' + result.error, 'error'); }
                } catch(e) { showToast('❌ Ошибка', 'error'); }
            }

            document.getElementById('privateMode').addEventListener('change', function() {
                fetch('/api/settings/private', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: this.checked })
                });
            });

            document.getElementById('admin2fa').addEventListener('change', function() {
                document.getElementById('faCodeGroup').style.display = this.checked ? 'block' : 'none';
                fetch('/api/settings/2fa', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: this.checked, code: document.getElementById('settings2faCode').value || '123456' })
                });
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    document.querySelectorAll('.modal.active').forEach(m => m.classList.remove('active'));
                }
                if (e.key === 'Enter') {
                    if (document.getElementById('addModal').classList.contains('active') && !document.getElementById('modalSubmitBtn').disabled) {
                        submitWin();
                    }
                    if (document.getElementById('deleteModal').classList.contains('active')) {
                        confirmDelete();
                    }
                }
            });

            // Автозагрузка при открытии
            document.addEventListener('DOMContentLoaded', () => {
                // Данные загрузятся при переходе на второй экран
            });
        </script>
    </body>
    </html>
    '''

# === API ===

@app.route('/api/wins')
def api_wins():
    data = load_data()
    return jsonify({'wins': data['wins']})

@app.route('/api/add', methods=['POST'])
def api_add():
    data = load_data()
    req = request.json
    user = req.get('user', '').strip()
    prize = req.get('prize', '').strip()
    value = req.get('value', 0)
    comment = req.get('comment', '').strip()
    if not user or not prize or value <= 0:
        return jsonify({'success': False, 'error': 'Заполните все поля'})
    win = {
        'id': data['next_id'],
        'user': user,
        'prize': prize,
        'value': value,
        'comment': comment,
        'likes': 0,
        'date': datetime.now().strftime('%d.%m.%Y %H:%M')
    }
    data['wins'].append(win)
    data['next_id'] += 1
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/delete', methods=['POST'])
def api_delete():
    data = load_data()
    win_id = request.json.get('id')
    new_wins = [w for w in data['wins'] if w['id'] != win_id]
    if len(new_wins) == len(data['wins']):
        return jsonify({'success': False, 'error': 'Запись не найдена'})
    data['wins'] = new_wins
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/user/<name>')
def api_user(name):
    data = load_data()
    user_wins = [w for w in data['wins'] if w['user'].lower() == name.lower()]
    return jsonify({
        'found': len(user_wins) > 0,
        'count': len(user_wins),
        'total_value': sum(w['value'] for w in user_wins),
        'wins': user_wins
    })

@app.route('/api/like', methods=['POST'])
def api_like():
    data = load_data()
    win_id = request.json.get('id')
    for w in data['wins']:
        if w['id'] == win_id:
            w['likes'] = w.get('likes', 0) + 1
            save_data(data)
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Не найдено'})

@app.route('/api/raffles')
def api_raffles():
    return jsonify(load_raffles())

@app.route('/api/raffle', methods=['POST'])
def api_raffle():
    raffles = load_raffles()
    req = request.json
    raffle = {
        'id': len(raffles) + 1,
        'title': req.get('title', ''),
        'prize': req.get('prize', ''),
        'value': req.get('value', 0),
        'type': req.get('type', 'standard'),
        'end_time': req.get('end_time', ''),
        'status': 'active',
        'participants': [],
        'created': datetime.now().strftime('%d.%m.%Y %H:%M')
    }
    raffles.append(raffle)
    save_raffles(raffles)
    return jsonify({'success': True})

@app.route('/api/raffle/join', methods=['POST'])
def api_join_raffle():
    raffles = load_raffles()
    req = request.json
    for r in raffles:
        if r['id'] == req.get('id'):
            if req.get('user') not in r['participants']:
                r['participants'].append(req.get('user'))
                save_raffles(raffles)
                return jsonify({'success': True})
            return jsonify({'success': False, 'error': 'Уже участвуете'})
    return jsonify({'success': False, 'error': 'Не найдено'})

@app.route('/api/announcements')
def api_announcements():
    data = load_announcements()
    return jsonify(data)

@app.route('/api/announcement', methods=['POST'])
def api_announcement():
    data = load_announcements()
    req = request.json
    data.append({
        'title': req.get('title', ''),
        'text': req.get('text', ''),
        'date': datetime.now().strftime('%d.%m.%Y %H:%M')
    })
    save_announcements(data)
    return jsonify({'success': True})

@app.route('/api/feedback')
def api_feedback():
    data = load_feedback()
    return jsonify(data)

@app.route('/api/feedback', methods=['POST'])
def api_feedback_post():
    data = load_feedback()
    req = request.json
    data.append({
        'user': req.get('user', 'Аноним'),
        'text': req.get('text', ''),
        'rating': req.get('rating', 5),
        'date': datetime.now().strftime('%d.%m.%Y %H:%M')
    })
    save_feedback(data)
    return jsonify({'success': True})

@app.route('/api/settings')
def api_settings():
    return jsonify(load_settings())

@app.route('/api/settings/code', methods=['POST'])
def api_settings_code():
    settings = load_settings()
    new_code = request.json.get('new_code', '')
    if len(new_code) < 4:
        return jsonify({'success': False, 'error': 'Код минимум 4 символа'})
    settings['code'] = new_code
    save_settings(settings)
    return jsonify({'success': True})

@app.route('/api/settings/private', methods=['POST'])
def api_settings_private():
    settings = load_settings()
    settings['private_mode'] = request.json.get('enabled', False)
    save_settings(settings)
    return jsonify({'success': True})

@app.route('/api/settings/2fa', methods=['POST'])
def api_settings_2fa():
    settings = load_settings()
    settings['admin_2fa'] = request.json.get('enabled', False)
    settings['admin_2fa_code'] = request.json.get('code', '123456')
    save_settings(settings)
    return jsonify({'success': True})

@app.route('/background')
def background():
    return send_file('background.jpg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
