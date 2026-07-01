from flask import Flask, send_file, request, jsonify, session
import os
import json
import hashlib
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'change-this-to-random-secret-key-12345'

# Файлы для хранения данных
USERS_FILE = 'users.json'
WINS_FILE = 'wins.json'
SHOP_FILE = 'shop.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_wins():
    if os.path.exists(WINS_FILE):
        with open(WINS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'wins': [], 'last_id': 0}

def save_wins(wins_data):
    with open(WINS_FILE, 'w', encoding='utf-8') as f:
        json.dump(wins_data, f, ensure_ascii=False, indent=2)

def load_shop():
    if os.path.exists(SHOP_FILE):
        with open(SHOP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'items': [
            {'id': 1, 'name': '👑 Победитель', 'price': 500, 'category': 'rank', 'icon': '👑'},
            {'id': 2, 'name': '⭐ Чемпион', 'price': 1000, 'category': 'rank', 'icon': '⭐'},
            {'id': 3, 'name': '🎖 Легенда', 'price': 2000, 'category': 'rank', 'icon': '🎖'},
            {'id': 4, 'name': '🖼 Золотая рамка', 'price': 300, 'category': 'frame', 'icon': '🖼'},
            {'id': 5, 'name': '🖼 Серебряная рамка', 'price': 200, 'category': 'frame', 'icon': '🖼'},
            {'id': 6, 'name': '🖼 Бронзовая рамка', 'price': 100, 'category': 'frame', 'icon': '🖼'},
            {'id': 7, 'name': '💎 Алмазная рамка', 'price': 500, 'category': 'frame', 'icon': '💎'},
            {'id': 8, 'name': '🐱 Аватарка Кот', 'price': 150, 'category': 'avatar', 'icon': '🐱'},
            {'id': 9, 'name': '🐶 Аватарка Пёс', 'price': 150, 'category': 'avatar', 'icon': '🐶'},
            {'id': 10, 'name': '🦊 Аватарка Лиса', 'price': 150, 'category': 'avatar', 'icon': '🦊'},
            {'id': 11, 'name': '🐲 Аватарка Дракон', 'price': 300, 'category': 'avatar', 'icon': '🐲'},
            {'id': 12, 'name': '🌈 Аватарка Радуга', 'price': 200, 'category': 'avatar', 'icon': '🌈'},
        ]
    }

def save_shop(shop_data):
    with open(SHOP_FILE, 'w', encoding='utf-8') as f:
        json.dump(shop_data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Требуется авторизация'}), 401
        return f(*args, **kwargs)
    return decorated_function

# === СТРАНИЦА 1: НАЧАЛЬНАЯ ===

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect_to_app()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AniCosmo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-image: url('/background');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                color: white;
                overflow: hidden;
                position: relative;
            }
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.55);
                z-index: 1;
            }
            .welcome-screen {
                position: relative;
                z-index: 10;
                text-align: center;
                padding: 20px;
                animation: fadeIn 1s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            .welcome-screen h1 {
                font-size: 52px;
                font-weight: 700;
                letter-spacing: 2px;
                text-shadow: 0 0 60px rgba(0,0,0,0.8);
                margin-bottom: 10px;
                background: linear-gradient(135deg, #f093fb, #f5576c);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .welcome-screen .subtitle {
                font-size: 20px;
                opacity: 0.6;
                letter-spacing: 4px;
                margin-bottom: 30px;
            }
            .welcome-screen .channel-block {
                margin-bottom: 45px;
            }
            .welcome-screen .channel-block .label {
                font-size: 16px;
                opacity: 0.5;
                letter-spacing: 3px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            .welcome-screen .channel-block a {
                font-size: 26px;
                color: #ff6b6b;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.3s;
                text-shadow: 0 0 30px rgba(255, 107, 107, 0.2);
            }
            .welcome-screen .channel-block a:hover {
                color: #ff8a8a;
            }
            .btn-start {
                padding: 16px 60px;
                font-size: 20px;
                font-weight: 500;
                letter-spacing: 3px;
                color: white;
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.25);
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
                backdrop-filter: blur(4px);
            }
            .btn-start:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.5);
                transform: scale(1.03);
                box-shadow: 0 0 40px rgba(255, 255, 255, 0.05);
            }
            .footer {
                position: fixed;
                bottom: 30px;
                left: 0;
                width: 100%;
                text-align: center;
                color: rgba(255,255,255,0.12);
                font-size: 13px;
                letter-spacing: 3px;
                z-index: 1;
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        
        <div class="welcome-screen">
            <h1>🌟 AniCosmo</h1>
            <div class="subtitle">Канал по Аникарду</div>
            <div class="channel-block">
                <div class="label">Канал</div>
                <a href="https://t.me/AniCosmoDay" target="_blank">@AniCosmoDay</a>
            </div>
            <button class="btn-start" onclick="window.location.href='/register-page'">Начать</button>
        </div>
        
        <div class="footer">ANICOSMO</div>
    </body>
    </html>
    '''

# === СТРАНИЦА 2: РЕГИСТРАЦИЯ ===

@app.route('/register-page')
def register_page():
    if 'user_id' in session:
        return redirect_to_app()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Регистрация - AniCosmo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-image: url('/background');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                color: white;
                position: relative;
            }
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.65);
                z-index: 1;
            }
            .register-box {
                position: relative;
                z-index: 10;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(20px);
                padding: 50px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                max-width: 450px;
                width: 100%;
                text-align: center;
                box-shadow: 0 30px 60px rgba(0,0,0,0.5);
                animation: fadeIn 0.8s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .register-box h2 {
                font-size: 32px;
                font-weight: 300;
                letter-spacing: 2px;
                margin-bottom: 30px;
                color: white;
            }
            .register-box .input-group {
                margin-bottom: 20px;
                text-align: left;
            }
            .register-box .input-group label {
                display: block;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 2px;
                opacity: 0.6;
                margin-bottom: 8px;
            }
            .register-box .input-group input {
                width: 100%;
                padding: 14px 18px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                color: white;
                font-size: 16px;
                transition: all 0.3s;
                outline: none;
            }
            .register-box .input-group input:focus {
                border-color: rgba(255, 107, 107, 0.5);
                background: rgba(255, 255, 255, 0.08);
                box-shadow: 0 0 30px rgba(255, 107, 107, 0.05);
            }
            .register-box .input-group input::placeholder {
                color: rgba(255, 255, 255, 0.2);
            }
            .register-box .btn-register {
                width: 100%;
                padding: 16px;
                font-size: 18px;
                font-weight: 500;
                letter-spacing: 2px;
                color: white;
                background: rgba(255, 107, 107, 0.3);
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
                margin-top: 10px;
            }
            .register-box .btn-register:hover {
                background: rgba(255, 107, 107, 0.5);
                border-color: rgba(255, 107, 107, 0.6);
                transform: scale(1.02);
            }
            .register-box .btn-register:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .btn-back {
                margin-top: 20px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: 400;
                letter-spacing: 2px;
                color: rgba(255,255,255,0.4);
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
            }
            .btn-back:hover {
                border-color: rgba(255, 255, 255, 0.3);
                color: white;
            }
            .message {
                margin-top: 15px;
                padding: 12px;
                border-radius: 10px;
                font-size: 14px;
                display: none;
            }
            .message.error {
                display: block;
                background: rgba(255, 0, 0, 0.2);
                border: 1px solid rgba(255, 0, 0, 0.3);
                color: #ff6b6b;
            }
            .message.success {
                display: block;
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid rgba(0, 255, 0, 0.2);
                color: #69db7c;
            }
            .ip-info {
                margin-top: 20px;
                font-size: 12px;
                opacity: 0.3;
                letter-spacing: 1px;
            }
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-10px); }
                75% { transform: translateX(10px); }
            }
            .shake {
                animation: shake 0.5s ease;
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        
        <div class="register-box">
            <h2>📝 Регистрация</h2>
            <form id="registerForm" onsubmit="register(event)">
                <div class="input-group">
                    <label>Ваше имя</label>
                    <input type="text" id="name" placeholder="Алексей" required>
                </div>
                <div class="input-group">
                    <label>Telegram ник</label>
                    <input type="text" id="telegram" placeholder="@Ale7xey" required>
                </div>
                <div class="input-group">
                    <label>Пароль</label>
                    <input type="password" id="password" placeholder="••••••••" required minlength="6">
                </div>
                <div id="message" class="message"></div>
                <button type="submit" class="btn-register" id="registerBtn">Зарегистрироваться</button>
            </form>
            <button class="btn-back" onclick="window.location.href='/'">← Назад</button>
            <div class="ip-info" id="ipDisplay">Загрузка IP...</div>
        </div>

        <script>
            // Показываем IP
            fetch('/get_ip')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('ipDisplay').textContent = 'IP: ' + data.ip;
                })
                .catch(() => {
                    document.getElementById('ipDisplay').textContent = 'IP: Не удалось определить';
                });

            function register(event) {
                event.preventDefault();

                const name = document.getElementById('name').value.trim();
                const telegram = document.getElementById('telegram').value.trim();
                const password = document.getElementById('password').value;
                const messageEl = document.getElementById('message');
                const btn = document.getElementById('registerBtn');

                if (!name || name.length < 2) {
                    showMessage('Имя должно содержать минимум 2 символа', 'error');
                    document.getElementById('name').classList.add('shake');
                    setTimeout(() => document.getElementById('name').classList.remove('shake'), 500);
                    return;
                }

                if (!telegram.startsWith('@') || telegram.length < 3) {
                    showMessage('Telegram ник должен начинаться с @', 'error');
                    document.getElementById('telegram').classList.add('shake');
                    setTimeout(() => document.getElementById('telegram').classList.remove('shake'), 500);
                    return;
                }

                if (password.length < 6) {
                    showMessage('Пароль должен быть минимум 6 символов', 'error');
                    document.getElementById('password').classList.add('shake');
                    setTimeout(() => document.getElementById('password').classList.remove('shake'), 500);
                    return;
                }

                btn.disabled = true;
                btn.textContent = 'Отправка...';

                fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, telegram, password })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showMessage('✅ ' + data.message, 'success');
                        btn.textContent = 'Успешно!';
                        setTimeout(() => {
                            window.location.href = '/app';
                        }, 1500);
                    } else {
                        showMessage('❌ ' + data.message, 'error');
                        btn.disabled = false;
                        btn.textContent = 'Зарегистрироваться';
                        document.querySelector('.register-box').classList.add('shake');
                        setTimeout(() => document.querySelector('.register-box').classList.remove('shake'), 500);
                    }
                })
                .catch(error => {
                    showMessage('Ошибка соединения с сервером', 'error');
                    btn.disabled = false;
                    btn.textContent = 'Зарегистрироваться';
                });
            }

            function showMessage(text, type) {
                const el = document.getElementById('message');
                el.textContent = text;
                el.className = 'message ' + type;
            }
        </script>
    </body>
    </html>
    '''

# === СТРАНИЦА 3: ОСНОВНОЕ ПРИЛОЖЕНИЕ ===

@app.route('/app')
def app_page():
    if 'user_id' not in session:
        return redirect_to_home()
    return redirect_to_app()

def redirect_to_app():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AniCosmo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 100vh;
                background-image: url('/background');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                color: white;
                padding: 20px;
                position: relative;
            }
            .overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.6);
                z-index: 0;
            }
            .container {
                max-width: 1200px;
                width: 100%;
                margin: 0 auto;
                position: relative;
                z-index: 1;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: rgba(0,0,0,0.3);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            .header h1 {
                font-size: 48px;
                font-weight: 700;
                background: linear-gradient(135deg, #f093fb, #f5576c);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 5px;
            }
            .header .subtitle {
                opacity: 0.6;
                font-size: 16px;
                letter-spacing: 2px;
            }
            .header .user-controls {
                margin-top: 15px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 15px;
                flex-wrap: wrap;
            }
            .header .user-controls a {
                color: #f5576c;
                text-decoration: none;
                font-size: 18px;
            }
            .btn-logout {
                padding: 8px 25px;
                background: rgba(255,107,107,0.2);
                border: 1px solid rgba(255,107,107,0.2);
                border-radius: 50px;
                color: white;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }
            .btn-logout:hover {
                background: rgba(255,107,107,0.3);
            }
            .main-menu {
                display: flex;
                justify-content: center;
                gap: 15px;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }
            .main-menu button {
                padding: 12px 30px;
                font-size: 16px;
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 50px;
                background: rgba(255,255,255,0.05);
                color: white;
                cursor: pointer;
                transition: all 0.3s;
                backdrop-filter: blur(10px);
                font-weight: 500;
                letter-spacing: 1px;
            }
            .main-menu button:hover {
                background: rgba(255,255,255,0.1);
                border-color: #f5576c;
                transform: translateY(-2px);
            }
            .main-menu button.active {
                background: rgba(245, 87, 108, 0.2);
                border-color: #f5576c;
            }
            .content {
                background: rgba(0,0,0,0.4);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 30px;
                border: 1px solid rgba(255,255,255,0.05);
                min-height: 400px;
                display: none;
            }
            .content.active {
                display: block;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                opacity: 0.3;
                font-size: 13px;
                letter-spacing: 3px;
            }
            .admin-panel {
                background: rgba(255,0,0,0.1);
                border: 1px solid rgba(255,0,0,0.2);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
            }
            .admin-panel h4 {
                color: #ff6b6b;
                margin-bottom: 15px;
            }
            .admin-panel input, .admin-panel select {
                padding: 10px;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                color: white;
                outline: none;
            }
            .admin-panel button {
                padding: 10px 20px;
                background: rgba(255,107,107,0.2);
                border: 1px solid rgba(255,107,107,0.2);
                border-radius: 10px;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }
            .admin-panel button:hover {
                background: rgba(255,107,107,0.3);
            }
            .shop-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .shop-item {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                transition: all 0.3s;
            }
            .shop-item:hover {
                transform: translateY(-5px);
                background: rgba(255,255,255,0.08);
            }
            .shop-item .icon {
                font-size: 40px;
            }
            .shop-item .name {
                margin: 10px 0;
                font-weight: 500;
            }
            .shop-item .price {
                color: #f5576c;
                font-weight: bold;
            }
            .shop-item .category-badge {
                font-size: 11px;
                opacity: 0.5;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .shop-item button {
                margin-top: 10px;
                padding: 8px 25px;
                background: rgba(245,87,108,0.3);
                border: 1px solid rgba(245,87,108,0.3);
                border-radius: 50px;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }
            .shop-item button:hover {
                background: rgba(245,87,108,0.5);
            }
            .shop-item .owned {
                color: #4ecdc4;
                font-size: 14px;
                margin-top: 5px;
            }
            .wins-list {
                max-height: 400px;
                overflow-y: auto;
            }
            .win-item {
                display: flex;
                justify-content: space-between;
                padding: 12px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                align-items: center;
            }
            .win-item .telegram { color: #4ecdc4; font-weight: bold; }
            .win-item .amount { color: #f5576c; font-weight: bold; }
            .win-item .prize { opacity: 0.7; }
            .win-item .date { opacity: 0.3; font-size: 12px; }
            .profile-info {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            .profile-card {
                background: rgba(255,255,255,0.05);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
            }
            .profile-card .value {
                font-size: 32px;
                font-weight: bold;
                margin: 10px 0;
            }
            .profile-card .label {
                opacity: 0.5;
                font-size: 14px;
            }
            .profile-avatar {
                font-size: 80px;
                text-align: center;
                margin-bottom: 20px;
            }
            .profile-frame {
                border: 3px solid #f5576c;
                border-radius: 20px;
                padding: 20px;
                display: inline-block;
            }
            .profile-rank {
                font-size: 24px;
                color: #ffe66d;
            }
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                z-index: 1000;
                justify-content: center;
                align-items: center;
            }
            .modal.active {
                display: flex;
            }
            .modal-content {
                background: #1a1a2e;
                padding: 40px;
                border-radius: 20px;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }
            .modal-content h3 {
                margin-bottom: 20px;
            }
            .modal-content input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                color: white;
                outline: none;
            }
            .modal-content button {
                padding: 12px 30px;
                background: rgba(245,87,108,0.3);
                border: 1px solid rgba(245,87,108,0.3);
                border-radius: 10px;
                color: white;
                cursor: pointer;
                margin: 5px;
            }
            .modal-content button:hover {
                background: rgba(245,87,108,0.5);
            }
            .modal-close {
                float: right;
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
            }
            .code-input {
                display: flex;
                gap: 10px;
                align-items: center;
                margin: 10px 0;
            }
            .code-input input {
                flex: 1;
            }
            .frame-preview {
                border: 3px solid #f5576c;
                border-radius: 15px;
                padding: 10px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">
            <div class="header">
                <h1>🌟 AniCosmo</h1>
                <div class="subtitle">Канал по Аникарду</div>
                <div class="user-controls">
                    <a href="https://t.me/AniCosmoDay" target="_blank">@AniCosmoDay</a>
                    <button class="btn-logout" onclick="logout()">Выйти</button>
                    <button class="btn-logout" onclick="showAdminPanel()" style="background: rgba(255,215,0,0.2); border-color: rgba(255,215,0,0.3);">🔑 Админ</button>
                </div>
            </div>

            <div class="main-menu">
                <button onclick="showSection('profile')" class="active" id="btn-profile">👤 Профиль</button>
                <button onclick="showSection('shop')" id="btn-shop">🛒 Магазин</button>
                <button onclick="showSection('wins')" id="btn-wins">🎰 Розыгрыши</button>
            </div>

            <div id="profile-section" class="content active"></div>
            <div id="shop-section" class="content"></div>
            <div id="wins-section" class="content"></div>

            <div class="footer">ANICOSMO</div>
        </div>

        <!-- Модальное окно админ-панели -->
        <div id="adminModal" class="modal">
            <div class="modal-content">
                <button class="modal-close" onclick="closeAdminPanel()">✕</button>
                <h3>🔐 Админ-панель</h3>
                <div class="code-input">
                    <input type="password" id="adminCode" placeholder="Введите код доступа">
                    <button onclick="checkAdminCode()">Войти</button>
                </div>
                <div id="adminContent" style="display: none; margin-top: 20px;">
                    <h4>📦 Управление магазином</h4>
                    <div style="margin: 10px 0;">
                        <input type="text" id="itemName" placeholder="Название">
                        <input type="number" id="itemPrice" placeholder="Цена в ПТ">
                        <select id="itemCategory">
                            <option value="rank">Звание</option>
                            <option value="frame">Рамка</option>
                            <option value="avatar">Аватарка</option>
                        </select>
                        <input type="text" id="itemIcon" placeholder="Иконка (эмодзи)">
                        <button onclick="addShopItem()">➕ Добавить</button>
                    </div>
                    <div id="shopItemsList"></div>
                    <hr style="margin: 20px 0;">
                    <h4>🎰 Управление выигрышами</h4>
                    <div style="margin: 10px 0;">
                        <input type="text" id="winTelegram" placeholder="@telegram">
                        <input type="text" id="winPrize" placeholder="Что выиграл">
                        <input type="number" id="winAmount" placeholder="Сумма в ПТ">
                        <button onclick="addWinAdmin()">➕ Добавить</button>
                    </div>
                    <div id="winsListAdmin"></div>
                </div>
            </div>
        </div>

        <script>
            let currentUser = null;
            let adminCode = '132547';

            function loadUserData() {
                fetch('/api/user')
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            currentUser = data.user;
                            renderProfile();
                            renderShop();
                            renderWins();
                        }
                    });
            }

            function showSection(section) {
                document.querySelectorAll('.content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.main-menu button').forEach(el => el.classList.remove('active'));
                
                document.getElementById(section + '-section').classList.add('active');
                document.getElementById('btn-' + section).classList.add('active');

                if (section === 'profile') renderProfile();
                if (section === 'shop') renderShop();
                if (section === 'wins') renderWins();
            }

            function renderProfile() {
                if (!currentUser) return;
                const section = document.getElementById('profile-section');
                const frame = currentUser.frame || '🖼';
                const avatar = currentUser.avatar || '👤';
                const rank = currentUser.rank || '';
                
                section.innerHTML = `
                    <div style="text-align: center;">
                        <div class="profile-frame" style="border-color: ${currentUser.frame_color || '#f5576c'}">
                            <div class="profile-avatar">${avatar}</div>
                        </div>
                        ${rank ? `<div class="profile-rank">${rank}</div>` : ''}
                        <h2 style="font-size: 28px; margin: 10px 0;">${currentUser.name}</h2>
                        <p style="opacity: 0.6; margin-bottom: 20px;">${currentUser.telegram}</p>
                        <div class="profile-info">
                            <div class="profile-card">
                                <div class="value" style="color: #f5576c;">${currentUser.points || 0}</div>
                                <div class="label">💰 ПТ Баллов</div>
                            </div>
                            <div class="profile-card">
                                <div class="value" style="color: #4ecdc4;">${currentUser.wins_count || 0}</div>
                                <div class="label">🏆 Побед</div>
                            </div>
                            <div class="profile-card">
                                <div class="value" style="color: #ffe66d; font-size: 20px;">${currentUser.rank || 'Нет звания'}</div>
                                <div class="label">⭐ Звание</div>
                            </div>
                        </div>
                        <div style="margin-top: 20px; opacity: 0.3; font-size: 12px;">
                            IP: ${currentUser.ip} • Зарегистрирован: ${new Date(currentUser.registered_at).toLocaleDateString()}
                        </div>
                    </div>
                `;
            }

            function renderShop() {
                const section = document.getElementById('shop-section');
                fetch('/api/shop')
                    .then(res => res.json())
                    .then(data => {
                        const itemsByCategory = {
                            rank: data.items.filter(i => i.category === 'rank'),
                            frame: data.items.filter(i => i.category === 'frame'),
                            avatar: data.items.filter(i => i.category === 'avatar')
                        };
                        
                        let html = `
                            <h2 style="margin-bottom: 20px;">🛒 Магазин</h2>
                            <p style="opacity: 0.6; margin-bottom: 20px;">Ваши баллы: <strong style="color: #f5576c;">${currentUser ? currentUser.points || 0 : 0} ПТ</strong></p>
                        `;

                        for (const [category, items] of Object.entries(itemsByCategory)) {
                            if (items.length === 0) continue;
                            const categoryNames = { rank: '⭐ Звания', frame: '🖼 Рамки', avatar: '🎨 Аватарки' };
                            html += `<h3 style="margin: 20px 0 10px 0;">${categoryNames[category] || category}</h3><div class="shop-grid">`;
                            items.forEach(item => {
                                const owned = currentUser && currentUser.purchases && currentUser.purchases.some(p => p.item_id === item.id);
                                html += `
                                    <div class="shop-item">
                                        <div class="icon">${item.icon}</div>
                                        <div class="name">${item.name}</div>
                                        <div class="category-badge">${category}</div>
                                        <div class="price">${item.price} ПТ</div>
                                        ${owned ? '<div class="owned">✅ Куплено</div>' : `<button onclick="buyItem(${item.id})">Купить</button>`}
                                    </div>
                                `;
                            });
                            html += `</div>`;
                        }
                        
                        section.innerHTML = html;
                    });
            }

            function renderWins() {
                const section = document.getElementById('wins-section');
                fetch('/api/wins')
                    .then(res => res.json())
                    .then(data => {
                        const recentWins = data.wins.slice(-10).reverse();
                        const topWins = [...data.wins].sort((a, b) => b.amount - a.amount).slice(0, 10);

                        section.innerHTML = `
                            <h2 style="margin-bottom: 20px;">🎰 Розыгрыши</h2>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                                <div>
                                    <h3 style="margin-bottom: 15px;">📋 Недавние выигрыши</h3>
                                    <div class="wins-list">
                                        ${recentWins.length === 0 ? '<p style="opacity: 0.3;">Пока нет выигрышей</p>' : recentWins.map(win => `
                                            <div class="win-item">
                                                <div>
                                                    <span class="telegram">${win.telegram}</span>
                                                    <span class="prize"> - ${win.prize}</span>
                                                </div>
                                                <div>
                                                    <span class="amount">+${win.amount} ПТ</span>
                                                    <span class="date">${new Date(win.date).toLocaleDateString()}</span>
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                <div>
                                    <h3 style="margin-bottom: 15px;">🏆 Топ по сумме ПТ</h3>
                                    <div class="wins-list">
                                        ${topWins.length === 0 ? '<p style="opacity: 0.3;">Нет данных</p>' : topWins.map((win, index) => `
                                            <div class="win-item">
                                                <div>
                                                    <span style="opacity: 0.5;">${index + 1}.</span>
                                                    <span class="telegram">${win.telegram}</span>
                                                </div>
                                                <div>
                                                    <span class="amount">${win.amount} ПТ</span>
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
            }

            function buyItem(itemId) {
                fetch('/api/buy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ ' + data.message);
                        loadUserData();
                        renderShop();
                    } else {
                        alert('❌ ' + data.message);
                    }
                });
            }

            function showAdminPanel() {
                document.getElementById('adminModal').classList.add('active');
                document.getElementById('adminContent').style.display = 'none';
                document.getElementById('adminCode').value = '';
            }

            function closeAdminPanel() {
                document.getElementById('adminModal').classList.remove('active');
            }

            function checkAdminCode() {
                const code = document.getElementById('adminCode').value;
                if (code === adminCode) {
                    document.getElementById('adminContent').style.display = 'block';
                    loadAdminShop();
                    loadAdminWins();
                } else {
                    alert('❌ Неверный код доступа!');
                }
            }

            function loadAdminShop() {
                fetch('/api/shop')
                    .then(res => res.json())
                    .then(data => {
                        const list = document.getElementById('shopItemsList');
                        list.innerHTML = data.items.map(item => `
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <span>${item.icon} ${item.name} - ${item.price} ПТ (${item.category})</span>
                                <button onclick="deleteShopItem(${item.id})" style="background: rgba(255,0,0,0.2); border: none; color: white; padding: 5px 15px; border-radius: 5px; cursor: pointer;">🗑</button>
                            </div>
                        `).join('');
                    });
            }

            function addShopItem() {
                const name = document.getElementById('itemName').value;
                const price = parseInt(document.getElementById('itemPrice').value);
                const category = document.getElementById('itemCategory').value;
                const icon = document.getElementById('itemIcon').value;

                if (!name || !price || !icon) {
                    alert('Заполните все поля!');
                    return;
                }

                fetch('/api/admin/shop/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, price, category, icon })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Товар добавлен!');
                        document.getElementById('itemName').value = '';
                        document.getElementById('itemPrice').value = '';
                        document.getElementById('itemIcon').value = '';
                        loadAdminShop();
                        renderShop();
                    } else {
                        alert('❌ ' + data.message);
                    }
                });
            }

            function deleteShopItem(itemId) {
                if (!confirm('Удалить товар?')) return;
                fetch('/api/admin/shop/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Товар удален!');
                        loadAdminShop();
                        renderShop();
                    } else {
                        alert('❌ ' + data.message);
                    }
                });
            }

            function loadAdminWins() {
                fetch('/api/wins')
                    .then(res => res.json())
                    .then(data => {
                        const list = document.getElementById('winsListAdmin');
                        list.innerHTML = data.wins.slice().reverse().slice(0, 20).map(win => `
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <span>${win.telegram} - ${win.prize} (+${win.amount} ПТ)</span>
                                <button onclick="deleteWin(${win.id})" style="background: rgba(255,0,0,0.2); border: none; color: white; padding: 5px 15px; border-radius: 5px; cursor: pointer;">🗑</button>
                            </div>
                        `).join('');
                    });
            }

            function addWinAdmin() {
                const telegram = document.getElementById('winTelegram').value;
                const prize = document.getElementById('winPrize').value;
                const amount = parseInt(document.getElementById('winAmount').value);

                if (!telegram || !prize || !amount) {
                    alert('Заполните все поля!');
                    return;
                }

                fetch('/api/admin/win/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ telegram, prize, amount })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Выигрыш добавлен!');
                        document.getElementById('winTelegram').value = '';
                        document.getElementById('winPrize').value = '';
                        document.getElementById('winAmount').value = '';
                        loadAdminWins();
                        renderWins();
                        loadUserData();
                    } else {
                        alert('❌ ' + data.message);
                    }
                });
            }

            function deleteWin(winId) {
                if (!confirm('Удалить выигрыш?')) return;
                fetch('/api/admin/win/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ win_id: winId })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Выигрыш удален!');
                        loadAdminWins();
                        renderWins();
                        loadUserData();
                    } else {
                        alert('❌ ' + data.message);
                    }
                });
            }

            function logout() {
                fetch('/logout')
                    .then(() => window.location.href = '/');
            }

            loadUserData();
            showSection('profile');
        </script>
    </body>
    </html>
    '''

def redirect_to_home():
    return '<script>window.location.href="/"</script>'

# === API ENDPOINTS ===

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Не авторизован'}), 401
    
    users = load_users()
    user = users.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    
    wins = load_wins()
    user_wins = [w for w in wins['wins'] if w['telegram'] == user['telegram']]
    
    return jsonify({
        'success': True,
        'user': {
            'name': user['name'],
            'telegram': user['telegram'],
            'points': user.get('points', 0),
            'wins_count': len(user_wins),
            'ip': user['ip'],
            'registered_at': user['registered_at'],
            'rank': user.get('rank', ''),
            'frame': user.get('frame', '🖼'),
            'frame_color': user.get('frame_color', '#f5576c'),
            'avatar': user.get('avatar', '👤'),
            'purchases': user.get('purchases', [])
        }
    })

@app.route('/api/shop')
def api_shop():
    shop = load_shop()
    return jsonify(shop)

@app.route('/api/buy', methods=['POST'])
@login_required
def api_buy():
    data = request.get_json()
    item_id = data.get('item_id')
    
    shop = load_shop()
    item = next((i for i in shop['items'] if i['id'] == item_id), None)
    if not item:
        return jsonify({'success': False, 'message': 'Товар не найден'})
    
    users = load_users()
    user = users.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})
    
    if 'purchases' in user:
        for p in user['purchases']:
            if p.get('item_id') == item_id:
                return jsonify({'success': False, 'message': 'У вас уже есть этот предмет!'})
    
    if user.get('points', 0) < item['price']:
        return jsonify({'success': False, 'message': f'Недостаточно баллов! Нужно {item["price"]} ПТ'})
    
    user['points'] = user.get('points', 0) - item['price']
    if 'purchases' not in user:
        user['purchases'] = []
    user['purchases'].append({
        'item_id': item['id'],
        'item_name': item['name'],
        'category': item['category'],
        'price': item['price'],
        'date': datetime.now().isoformat()
    })
    
    if item['category'] == 'rank':
        user['rank'] = item['name']
    elif item['category'] == 'frame':
        user['frame'] = item['icon']
        user['frame_color'] = '#ffd700' if 'Золотая' in item['name'] else '#c0c0c0' if 'Серебряная' in item['name'] else '#cd7f32' if 'Бронзовая' in item['name'] else '#00ffff' if 'Алмазная' in item['name'] else '#f5576c'
    elif item['category'] == 'avatar':
        user['avatar'] = item['icon']
    
    save_users(users)
    return jsonify({'success': True, 'message': f'Вы купили {item["name"]}!'})

@app.route('/api/wins')
def api_wins():
    wins = load_wins()
    return jsonify(wins)

# === АДМИН API ===

@app.route('/api/admin/shop/add', methods=['POST'])
@login_required
def admin_add_shop():
    data = request.get_json()
    shop = load_shop()
    
    new_id = max([i['id'] for i in shop['items']]) + 1 if shop['items'] else 1
    shop['items'].append({
        'id': new_id,
        'name': data['name'],
        'price': data['price'],
        'category': data['category'],
        'icon': data['icon']
    })
    save_shop(shop)
    return jsonify({'success': True, 'message': 'Товар добавлен'})

@app.route('/api/admin/shop/delete', methods=['POST'])
@login_required
def admin_delete_shop():
    data = request.get_json()
    shop = load_shop()
    shop['items'] = [i for i in shop['items'] if i['id'] != data['item_id']]
    save_shop(shop)
    return jsonify({'success': True, 'message': 'Товар удален'})

@app.route('/api/admin/win/add', methods=['POST'])
@login_required
def admin_add_win():
    data = request.get_json()
    telegram = data.get('telegram', '').strip()
    prize = data.get('prize', '').strip()
    amount = data.get('amount', 0)
    
    if not telegram.startswith('@'):
        return jsonify({'success': False, 'message': 'Telegram ник должен начинаться с @'})
    
    if not prize or amount <= 0:
        return jsonify({'success': False, 'message': 'Заполните все поля корректно'})
    
    wins = load_wins()
    wins['last_id'] += 1
    
    win_entry = {
        'id': wins['last_id'],
        'telegram': telegram,
        'prize': prize,
        'amount': amount,
        'date': datetime.now().isoformat(),
        'added_by': session.get('user_name', 'admin')
    }
    
    wins['wins'].append(win_entry)
    save_wins(wins)
    
    users = load_users()
    for user_id, user in users.items():
        if user['telegram'] == telegram:
            user['points'] = user.get('points', 0) + amount
            user['last_win'] = datetime.now().isoformat()
            save_users(users)
            break
    
    return jsonify({'success': True, 'message': 'Выигрыш добавлен!'})

@app.route('/api/admin/win/delete', methods=['POST'])
@login_required
def admin_delete_win():
    data = request.get_json()
    win_id = data.get('win_id')
    
    wins = load_wins()
    win_to_delete = next((w for w in wins['wins'] if w['id'] == win_id), None)
    if win_to_delete:
        users = load_users()
        for user_id, user in users.items():
            if user['telegram'] == win_to_delete['telegram']:
                user['points'] = user.get('points', 0) - win_to_delete['amount']
                if user['points'] < 0:
                    user['points'] = 0
                save_users(users)
                break
    
    wins['wins'] = [w for w in wins['wins'] if w['id'] != win_id]
    save_wins(wins)
    return jsonify({'success': True, 'message': 'Выигрыш удален'})

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        telegram = data.get('telegram', '').strip()
        password = data.get('password', '')
        
        if not name or len(name) < 2:
            return jsonify({'success': False, 'message': 'Имя слишком короткое'})
        
        if not telegram.startswith('@') or len(telegram) < 3:
            return jsonify({'success': False, 'message': 'Неверный формат Telegram ника'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Пароль должен быть минимум 6 символов'})
        
        users = load_users()
        client_ip = get_client_ip()
        
        ip_registrations = [u for u in users.values() if u.get('ip') == client_ip]
        if len(ip_registrations) >= 1:
            return jsonify({'success': False, 'message': '⚠️ С этого IP уже зарегистрирован аккаунт!'})
        
        for user_id, user_data in users.items():
            if user_data.get('telegram') == telegram:
                return jsonify({'success': False, 'message': 'Этот Telegram уже зарегистрирован'})
        
        user_id = str(len(users) + 1)
        users[user_id] = {
            'name': name,
            'telegram': telegram,
            'password_hash': hash_password(password),
            'ip': client_ip,
            'points': 100,
            'registered_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'purchases': [],
            'rank': '',
            'frame': '🖼',
            'frame_color': '#f5576c',
            'avatar': '👤'
        }
        
        save_users(users)
        session['user_id'] = user_id
        session['user_name'] = name
        
        return jsonify({
            'success': True,
            'message': f'Добро пожаловать, {name}! Вы получили 100 ПТ бонуса!',
            'redirect': '/app'
        })
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({'success': False, 'message': 'Ошибка на сервере'})

@app.route('/logout')
def logout():
    session.clear()
    return '', 200

@app.route('/background')
def background():
    try:
        return send_file('background.jpg')
    except:
        from flask import Response
        import io
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (1920, 1080), color=(15, 12, 41))
        draw = ImageDraw.Draw(img)
        for i in range(0, 1080, 30):
            draw.rectangle([0, i, 1920, i+15], fill=(48, 43, 99))
        for i in range(0, 1920, 40):
            draw.rectangle([i, 0, i+20, 1080], fill=(48, 43, 99, 50))
        
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=85)
        img_io.seek(0)
        return Response(img_io.getvalue(), mimetype='image/jpeg')

@app.route('/get_ip')
def get_ip():
    return jsonify({'ip': get_client_ip()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
