from flask import Flask, send_file, request, jsonify, session
import os
import json
import hashlib
from datetime import datetime
from functools import wraps
import sys
import random

app = Flask(__name__)
app.secret_key = 'change-this-to-random-secret-key-12345'

# === ОПРЕДЕЛЕНИЕ ПАПКИ ДЛЯ ДАННЫХ ===
def get_data_dir():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    try:
        os.makedirs(data_dir, exist_ok=True)
        test_file = os.path.join(data_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✅ Используем папку: {data_dir}")
        return data_dir
    except Exception as e:
        print(f"❌ Нет прав на запись в {data_dir}: {e}")
        data_dir = '/tmp/anicospo_data'
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"⚠️ Используем временную папку: {data_dir}")
            return data_dir
        except Exception as e2:
            print(f"❌ Нет прав на запись в /tmp/: {e2}")
            data_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"⚠️ Используем папку: {data_dir}")
            return data_dir

DATA_DIR = get_data_dir()

def get_file_path(filename):
    return os.path.join(DATA_DIR, filename)

def init_files():
    files = {
        'users.json': {},
        'wins.json': {'wins': [], 'last_id': 0},
        'shop.json': {
            'items': [
                # Звания
                {'id': 1, 'name': '👑 Победитель', 'price': 500, 'category': 'rank', 'icon': '👑', 'color': '#ffe66d'},
                {'id': 2, 'name': '⭐ Чемпион', 'price': 1000, 'category': 'rank', 'icon': '⭐', 'color': '#ffd700'},
                {'id': 3, 'name': '🎖 Легенда', 'price': 2000, 'category': 'rank', 'icon': '🎖', 'color': '#ff6b6b'},
                # Рамки с цветами
                {'id': 4, 'name': '🖼 Золотая рамка', 'price': 300, 'category': 'frame', 'icon': '🖼', 'color': '#ffd700'},
                {'id': 5, 'name': '🖼 Серебряная рамка', 'price': 200, 'category': 'frame', 'icon': '🖼', 'color': '#c0c0c0'},
                {'id': 6, 'name': '🖼 Бронзовая рамка', 'price': 100, 'category': 'frame', 'icon': '🖼', 'color': '#cd7f32'},
                {'id': 7, 'name': '💎 Алмазная рамка', 'price': 500, 'category': 'frame', 'icon': '💎', 'color': '#00ffff'},
                {'id': 13, 'name': '🖼 Угольная рамка', 'price': 350, 'category': 'frame', 'icon': '🖼', 'color': '#2f2f2f'},
                {'id': 14, 'name': '🖼 Изумрудная рамка', 'price': 400, 'category': 'frame', 'icon': '🖼', 'color': '#50c878'},
                {'id': 15, 'name': '🖼 Рубиновая рамка', 'price': 450, 'category': 'frame', 'icon': '🖼', 'color': '#e0115f'},
                {'id': 16, 'name': '🖼 Неоновая рамка', 'price': 300, 'category': 'frame', 'icon': '🖼', 'color': '#ff00ff'},
                # Аватарки
                {'id': 8, 'name': '🐱 Аватарка Кот', 'price': 150, 'category': 'avatar', 'icon': '🐱', 'color': None},
                {'id': 9, 'name': '🐶 Аватарка Пёс', 'price': 150, 'category': 'avatar', 'icon': '🐶', 'color': None},
                {'id': 10, 'name': '🦊 Аватарка Лиса', 'price': 150, 'category': 'avatar', 'icon': '🦊', 'color': None},
                {'id': 11, 'name': '🐲 Аватарка Дракон', 'price': 300, 'category': 'avatar', 'icon': '🐲', 'color': None},
                {'id': 12, 'name': '🌈 Аватарка Радуга', 'price': 200, 'category': 'avatar', 'icon': '🌈', 'color': None},
                {'id': 17, 'name': '🐼 Аватарка Панда', 'price': 200, 'category': 'avatar', 'icon': '🐼', 'color': None},
                {'id': 18, 'name': '🦄 Аватарка Единорог', 'price': 250, 'category': 'avatar', 'icon': '🦄', 'color': None},
                {'id': 19, 'name': '🐧 Аватарка Пингвин', 'price': 150, 'category': 'avatar', 'icon': '🐧', 'color': None},
                {'id': 20, 'name': '🦁 Аватарка Лев', 'price': 300, 'category': 'avatar', 'icon': '🦁', 'color': None},
                # Карты
                {'id': 21, 'name': '♠️ Туз пик', 'price': 500, 'category': 'card', 'icon': '♠️', 'color': None},
                {'id': 22, 'name': '♥️ Король червей', 'price': 600, 'category': 'card', 'icon': '♥️', 'color': None},
                {'id': 23, 'name': '♦️ Дама бубен', 'price': 400, 'category': 'card', 'icon': '♦️', 'color': None},
                {'id': 24, 'name': '♣️ Валет треф', 'price': 350, 'category': 'card', 'icon': '♣️', 'color': None},
                {'id': 25, 'name': '🃏 Джокер', 'price': 1000, 'category': 'card', 'icon': '🃏', 'color': None},
            ]
        },
        'admin_code.txt': '132547',
        'competitions.json': {'competitions': [], 'last_id': 0}
    }
    
    for filename, default_content in files.items():
        filepath = get_file_path(filename)
        if not os.path.exists(filepath):
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    if isinstance(default_content, (dict, list)):
                        json.dump(default_content, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(str(default_content))
                print(f"✅ Создан файл: {filename}")
            except Exception as e:
                print(f"❌ Не удалось создать {filename}: {e}")

init_files()

# === ОСТАЛЬНЫЕ ФУНКЦИИ ===

def get_admin_code():
    try:
        filepath = get_file_path('admin_code.txt')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except:
        pass
    return '132547'

def load_users():
    try:
        filepath = get_file_path('users.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки users.json: {e}")
    return {}

def save_users(users):
    try:
        filepath = get_file_path('users.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения users.json: {e}")
        return False

def load_wins():
    try:
        filepath = get_file_path('wins.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {'wins': [], 'last_id': 0}

def save_wins(wins_data):
    try:
        filepath = get_file_path('wins.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(wins_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_shop():
    try:
        filepath = get_file_path('shop.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {'items': []}

def save_shop(shop_data):
    try:
        filepath = get_file_path('shop.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(shop_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_competitions():
    try:
        filepath = get_file_path('competitions.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {'competitions': [], 'last_id': 0}

def save_competitions(comp_data):
    try:
        filepath = get_file_path('competitions.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comp_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Требуется авторизация'}), 401
        users = load_users()
        user = users.get(session['user_id'])
        if not user or not user.get('is_admin', False):
            return jsonify({'success': False, 'message': 'Требуются права администратора'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ВСЕ МАРШРУТЫ
# ==========================================

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
            .welcome-screen .buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .btn-start, .btn-login {
                padding: 16px 40px;
                font-size: 18px;
                font-weight: 500;
                letter-spacing: 2px;
                color: white;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
                backdrop-filter: blur(4px);
            }
            .btn-start {
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.25);
            }
            .btn-start:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.5);
                transform: scale(1.03);
                box-shadow: 0 0 40px rgba(255, 255, 255, 0.05);
            }
            .btn-login {
                background: rgba(245, 87, 108, 0.2);
                border: 2px solid rgba(245, 87, 108, 0.3);
            }
            .btn-login:hover {
                background: rgba(245, 87, 108, 0.3);
                border-color: rgba(245, 87, 108, 0.5);
                transform: scale(1.03);
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
            <div class="buttons">
                <button class="btn-start" onclick="window.location.href='/register-page'">Регистрация</button>
                <button class="btn-login" onclick="window.location.href='/login-page'">Вход</button>
            </div>
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
                    <input type="text" id="name" placeholder="Введите ваше имя" required>
                </div>
                <div class="input-group">
                    <label>Telegram ник</label>
                    <input type="text" id="telegram" placeholder="@username" required>
                </div>
                <div class="input-group">
                    <label>Пароль</label>
                    <input type="password" id="password" placeholder="Минимум 6 символов" required minlength="6">
                </div>
                <div id="message" class="message"></div>
                <button type="submit" class="btn-register" id="registerBtn">Зарегистрироваться</button>
            </form>
            <button class="btn-back" onclick="window.location.href='/'">← Назад</button>
            <div class="ip-info" id="ipDisplay">Загрузка IP...</div>
        </div>

        <script>
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

# === СТРАНИЦА 3: ВХОД ===

@app.route('/login-page')
def login_page():
    if 'user_id' in session:
        return redirect_to_app()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Вход - AniCosmo</title>
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
            .login-box {
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
            .login-box h2 {
                font-size: 32px;
                font-weight: 300;
                letter-spacing: 2px;
                margin-bottom: 30px;
                color: white;
            }
            .login-box .input-group {
                margin-bottom: 20px;
                text-align: left;
            }
            .login-box .input-group label {
                display: block;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 2px;
                opacity: 0.6;
                margin-bottom: 8px;
            }
            .login-box .input-group input {
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
            .login-box .input-group input:focus {
                border-color: rgba(255, 107, 107, 0.5);
                background: rgba(255, 255, 255, 0.08);
                box-shadow: 0 0 30px rgba(255, 107, 107, 0.05);
            }
            .login-box .input-group input::placeholder {
                color: rgba(255, 255, 255, 0.2);
            }
            .login-box .btn-login {
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
            .login-box .btn-login:hover {
                background: rgba(255, 107, 107, 0.5);
                border-color: rgba(255, 107, 107, 0.6);
                transform: scale(1.02);
            }
            .login-box .btn-login:disabled {
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
        
        <div class="login-box">
            <h2>🔐 Вход</h2>
            <form id="loginForm" onsubmit="login(event)">
                <div class="input-group">
                    <label>Telegram ник</label>
                    <input type="text" id="telegram" placeholder="@username" required>
                </div>
                <div class="input-group">
                    <label>Пароль</label>
                    <input type="password" id="password" placeholder="••••••••" required>
                </div>
                <div id="message" class="message"></div>
                <button type="submit" class="btn-login" id="loginBtn">Войти</button>
            </form>
            <button class="btn-back" onclick="window.location.href='/'">← Назад</button>
        </div>

        <script>
            function login(event) {
                event.preventDefault();

                const telegram = document.getElementById('telegram').value.trim();
                const password = document.getElementById('password').value;
                const messageEl = document.getElementById('message');
                const btn = document.getElementById('loginBtn');

                if (!telegram.startsWith('@') || telegram.length < 3) {
                    showMessage('Telegram ник должен начинаться с @', 'error');
                    document.getElementById('telegram').classList.add('shake');
                    setTimeout(() => document.getElementById('telegram').classList.remove('shake'), 500);
                    return;
                }

                if (!password || password.length < 6) {
                    showMessage('Введите пароль', 'error');
                    document.getElementById('password').classList.add('shake');
                    setTimeout(() => document.getElementById('password').classList.remove('shake'), 500);
                    return;
                }

                btn.disabled = true;
                btn.textContent = 'Вход...';

                fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ telegram, password })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showMessage('✅ ' + data.message, 'success');
                        btn.textContent = 'Успешно!';
                        setTimeout(() => {
                            window.location.href = '/app';
                        }, 1000);
                    } else {
                        showMessage('❌ ' + data.message, 'error');
                        btn.disabled = false;
                        btn.textContent = 'Войти';
                        document.querySelector('.login-box').classList.add('shake');
                        setTimeout(() => document.querySelector('.login-box').classList.remove('shake'), 500);
                    }
                })
                .catch(error => {
                    showMessage('Ошибка соединения с сервером', 'error');
                    btn.disabled = false;
                    btn.textContent = 'Войти';
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

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def redirect_to_app():
    return '<script>window.location.href="/app"</script>'

def redirect_to_home():
    return '<script>window.location.href="/"</script>'

# === СТРАНИЦА 4: ОСНОВНОЕ ПРИЛОЖЕНИЕ ===

@app.route('/app')
def app_page():
    if 'user_id' not in session:
        return redirect_to_home()
    
    users = load_users()
    user = users.get(session['user_id'])
    is_admin = user.get('is_admin', False) if user else False
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AniCosmo</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 100vh;
                background-image: url('/background');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                color: white;
                padding: 20px;
                position: relative;
            }}
            .overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.6);
                z-index: 0;
            }}
            .container {{
                max-width: 1200px;
                width: 100%;
                margin: 0 auto;
                position: relative;
                z-index: 1;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: rgba(0,0,0,0.3);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }}
            .header h1 {{
                font-size: 48px;
                font-weight: 700;
                background: linear-gradient(135deg, #f093fb, #f5576c);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 5px;
            }}
            .header .subtitle {{
                opacity: 0.6;
                font-size: 16px;
                letter-spacing: 2px;
            }}
            .header .user-controls {{
                margin-top: 15px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 15px;
                flex-wrap: wrap;
            }}
            .header .user-controls a {{
                color: #f5576c;
                text-decoration: none;
                font-size: 18px;
            }}
            .btn-logout {{
                padding: 8px 25px;
                background: rgba(255,107,107,0.2);
                border: 1px solid rgba(255,107,107,0.2);
                border-radius: 50px;
                color: white;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }}
            .btn-logout:hover {{
                background: rgba(255,107,107,0.3);
            }}
            .main-menu {{
                display: flex;
                justify-content: center;
                gap: 15px;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }}
            .main-menu button {{
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
            }}
            .main-menu button:hover {{
                background: rgba(255,255,255,0.1);
                border-color: #f5576c;
                transform: translateY(-2px);
            }}
            .main-menu button.active {{
                background: rgba(245, 87, 108, 0.2);
                border-color: #f5576c;
            }}
            .content {{
                background: rgba(0,0,0,0.4);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 30px;
                border: 1px solid rgba(255,255,255,0.05);
                min-height: 400px;
                display: none;
            }}
            .content.active {{
                display: block;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                opacity: 0.3;
                font-size: 13px;
                letter-spacing: 3px;
            }}
            .shop-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .shop-item {{
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                transition: all 0.3s;
            }}
            .shop-item:hover {{
                transform: translateY(-5px);
                background: rgba(255,255,255,0.08);
            }}
            .shop-item .icon {{
                font-size: 40px;
            }}
            .shop-item .name {{
                margin: 10px 0;
                font-weight: 500;
            }}
            .shop-item .price {{
                color: #f5576c;
                font-weight: bold;
            }}
            .shop-item .category-badge {{
                font-size: 11px;
                opacity: 0.5;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .shop-item button {{
                margin-top: 10px;
                padding: 8px 25px;
                background: rgba(245,87,108,0.3);
                border: 1px solid rgba(245,87,108,0.3);
                border-radius: 50px;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
                margin-right: 5px;
            }}
            .shop-item button:hover {{
                background: rgba(245,87,108,0.5);
            }}
            .shop-item .owned {{
                color: #4ecdc4;
                font-size: 14px;
                margin-top: 5px;
            }}
            .shop-item .selected-badge {{
                color: #ffe66d;
                font-size: 14px;
                margin-top: 5px;
                border: 1px solid #ffe66d;
                border-radius: 10px;
                padding: 2px 10px;
                display: inline-block;
            }}
            .wins-list {{
                max-height: 400px;
                overflow-y: auto;
            }}
            .win-item {{
                display: flex;
                justify-content: space-between;
                padding: 12px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                align-items: center;
            }}
            .win-item .telegram {{ color: #4ecdc4; font-weight: bold; cursor: pointer; }}
            .win-item .telegram:hover {{ text-decoration: underline; }}
            .win-item .amount {{ color: #f5576c; font-weight: bold; }}
            .win-item .prize {{ opacity: 0.7; }}
            .win-item .date {{ opacity: 0.3; font-size: 12px; }}
            .profile-info {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            .profile-card {{
                background: rgba(255,255,255,0.05);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .profile-card:hover {{
                background: rgba(255,255,255,0.1);
                transform: scale(1.02);
            }}
            .profile-card .value {{
                font-size: 32px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .profile-card .label {{
                opacity: 0.5;
                font-size: 14px;
            }}
            .profile-avatar {{
                font-size: 80px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .profile-frame {{
                border: 3px solid #f5576c;
                border-radius: 20px;
                padding: 20px;
                display: inline-block;
            }}
            .profile-rank {{
                font-size: 24px;
                color: #ffe66d;
            }}
            .modal {{
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
            }}
            .modal.active {{
                display: flex;
            }}
            .modal-content {{
                background: #1a1a2e;
                padding: 40px;
                border-radius: 20px;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }}
            .modal-content h3 {{
                margin-bottom: 20px;
            }}
            .modal-content input {{
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                color: white;
                outline: none;
            }}
            .modal-content button {{
                padding: 12px 30px;
                background: rgba(245,87,108,0.3);
                border: 1px solid rgba(245,87,108,0.3);
                border-radius: 10px;
                color: white;
                cursor: pointer;
                margin: 5px;
            }}
            .modal-content button:hover {{
                background: rgba(245,87,108,0.5);
            }}
            .modal-close {{
                float: right;
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
            }}
            .code-input {{
                display: flex;
                gap: 10px;
                align-items: center;
                margin: 10px 0;
            }}
            .code-input input {{
                flex: 1;
            }}
            .users-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .user-card {{
                background: rgba(255,255,255,0.05);
                padding: 15px;
                border-radius: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .user-card:hover {{
                background: rgba(255,255,255,0.1);
                transform: scale(1.02);
            }}
            .user-card .user-info {{
                display: flex;
                flex-direction: column;
            }}
            .user-card .user-name {{
                font-weight: bold;
            }}
            .user-card .user-telegram {{
                opacity: 0.5;
                font-size: 14px;
            }}
            .user-card .user-stats {{
                font-size: 12px;
                opacity: 0.6;
            }}
            .user-card .admin-badge {{
                background: rgba(255,215,0,0.2);
                color: #ffd700;
                padding: 2px 10px;
                border-radius: 10px;
                font-size: 11px;
            }}
            .user-card .make-admin-btn {{
                background: rgba(255,215,0,0.2);
                border: 1px solid rgba(255,215,0,0.3);
                color: white;
                padding: 5px 15px;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .user-card .make-admin-btn:hover {{
                background: rgba(255,215,0,0.3);
            }}
            .admin-crown {{
                color: #ffd700;
                font-size: 20px;
                margin-left: 5px;
            }}
            /* Стили для мини-игр */
            .game-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .game-card {{
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .game-card:hover {{
                transform: scale(1.05);
                background: rgba(255,255,255,0.1);
            }}
            .game-card .game-icon {{
                font-size: 60px;
                margin-bottom: 10px;
            }}
            .game-card .game-name {{
                font-size: 20px;
                font-weight: bold;
            }}
            .game-card .game-checkbox {{
                margin-top: 10px;
            }}
            .game-card input[type="checkbox"] {{
                width: 20px;
                height: 20px;
                cursor: pointer;
                accent-color: #f5576c;
            }}
            .game-card .game-count {{
                margin-top: 10px;
            }}
            .game-card .game-count input {{
                width: 80px;
                padding: 5px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                color: white;
                text-align: center;
            }}
            .game-result {{
                margin-top: 20px;
                padding: 20px;
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                display: none;
            }}
            .game-result.active {{
                display: block;
            }}
            .winner-text {{
                font-size: 24px;
                color: #ffe66d;
            }}
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
                <button onclick="showSection('games')" id="btn-games">🎮 Игры</button>
                <button onclick="showSection('wins')" id="btn-wins">🎰 Розыгрыши</button>
                <button onclick="showSection('top')" id="btn-top">🏆 Топ</button>
                <button onclick="showSection('competitions')" id="btn-competitions">🏆 Соревнования</button>
            </div>

            <div id="profile-section" class="content active"></div>
            <div id="shop-section" class="content"></div>
            <div id="games-section" class="content"></div>
            <div id="wins-section" class="content"></div>
            <div id="top-section" class="content"></div>
            <div id="competitions-section" class="content"></div>

            <div class="footer">ANICOSMO</div>
        </div>

        <!-- Модальное окно профиля пользователя -->
        <div id="userProfileModal" class="modal">
            <div class="modal-content">
                <button class="modal-close" onclick="closeUserProfile()">✕</button>
                <div id="userProfileContent"></div>
            </div>
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
                    <h4>📋 Все участники</h4>
                    <div id="usersList"></div>
                    <hr style="margin: 20px 0;">
                    <h4>🔑 Смена кода</h4>
                    <div style="margin: 10px 0;">
                        <input type="password" id="oldCode" placeholder="Старый код">
                        <input type="password" id="newCode" placeholder="Новый код">
                        <button onclick="changeCode()">Изменить код</button>
                    </div>
                    <hr style="margin: 20px 0;">
                    <h4>📦 Управление магазином</h4>
                    <div style="margin: 10px 0;">
                        <input type="text" id="itemName" placeholder="Название">
                        <input type="number" id="itemPrice" placeholder="Цена в ПТ">
                        <select id="itemCategory">
                            <option value="rank">Звание</option>
                            <option value="frame">Рамка</option>
                            <option value="avatar">Аватарка</option>
                            <option value="card">Карта</option>
                        </select>
                        <input type="text" id="itemIcon" placeholder="Иконка (эмодзи)">
                        <input type="text" id="itemColor" placeholder="Цвет рамки (например #ff0000) или оставить пустым">
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
                    <hr style="margin: 20px 0;">
                    <h4>🏆 Соревнования</h4>
                    <div style="margin: 10px 0; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                        <h5 style="margin-bottom: 10px;">Создать соревнование</h5>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <input type="text" id="compName" placeholder="Название (например: Турнир по футбику)">
                            <input type="number" id="compPoints" placeholder="Очков за победу" value="10">
                        </div>
                        <div style="margin: 10px 0;">
                            <label style="font-size: 12px; opacity: 0.5;">Игры (через запятую):</label>
                            <input type="text" id="compGames" placeholder="футбик, баскет, казино, дартс" style="width: 100%;">
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0;">
                            <input type="text" id="compPrize" placeholder="Приз (например: 👑 Суперчемпион)">
                            <input type="number" id="compPrizeValue" placeholder="Стоимость приза" value="0">
                            <select id="compPrizeType">
                                <option value="points">ПТ баллы</option>
                                <option value="rank">Звание</option>
                                <option value="frame">Рамка</option>
                                <option value="avatar">Аватарка</option>
                            </select>
                        </div>
                        <button onclick="createCompetition()" style="width: 100%;">➕ Создать соревнование</button>
                    </div>
                    <div id="competitionsListAdmin"></div>
                </div>
            </div>
        </div>

        <script>
            let currentUser = null;
            let currentAdminCode = '';
            let isAdmin = {str(is_admin).lower()};

            function loadUserData() {{
                fetch('/api/user')
                    .then(res => res.json())
                    .then(data => {{
                        if (data.success) {{
                            currentUser = data.user;
                            renderProfile();
                            renderShop();
                            renderGames();
                            renderWins();
                            renderTop();
                            renderCompetitions();
                        }}
                    }});
            }}

            function showSection(section) {{
                document.querySelectorAll('.content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.main-menu button').forEach(el => el.classList.remove('active'));
                
                document.getElementById(section + '-section').classList.add('active');
                document.getElementById('btn-' + section).classList.add('active');

                if (section === 'profile') renderProfile();
                if (section === 'shop') renderShop();
                if (section === 'games') renderGames();
                if (section === 'wins') renderWins();
                if (section === 'top') renderTop();
                if (section === 'competitions') renderCompetitions();
            }}

            function renderProfile() {{
                if (!currentUser) return;
                const section = document.getElementById('profile-section');
                const avatar = currentUser.avatar || '👤';
                const rank = currentUser.rank || '';
                const isAdminUser = currentUser.is_admin || false;
                
                section.innerHTML = `
                    <div style="text-align: center;">
                        <div class="profile-frame" style="border-color: ${{currentUser.frame_color || '#f5576c'}}">
                            <div class="profile-avatar">${{avatar}}</div>
                        </div>
                        ${{rank ? `<div class="profile-rank">${{rank}}</div>` : ''}}
                        <h2 style="font-size: 28px; margin: 10px 0;">
                            ${{currentUser.name}}
                            ${{isAdminUser ? '<span class="admin-crown">👑</span>' : ''}}
                        </h2>
                        <p style="opacity: 0.6; margin-bottom: 20px;">${{currentUser.telegram}}</p>
                        <div class="profile-info">
                            <div class="profile-card">
                                <div class="value" style="color: #f5576c;">${{currentUser.points || 0}}</div>
                                <div class="label">💰 ПТ Баллов</div>
                            </div>
                            <div class="profile-card">
                                <div class="value" style="color: #4ecdc4;">${{currentUser.wins_count || 0}}</div>
                                <div class="label">🏆 Побед</div>
                            </div>
                            <div class="profile-card">
                                <div class="value" style="color: #ffe66d; font-size: 20px;">${{currentUser.rank || 'Нет звания'}}</div>
                                <div class="label">⭐ Звание</div>
                            </div>
                        </div>
                        <div style="margin-top: 20px; opacity: 0.3; font-size: 12px;">
                            IP: ${{currentUser.ip}} • Зарегистрирован: ${{new Date(currentUser.registered_at).toLocaleDateString()}}
                            ${{isAdminUser ? ' • 👑 Администратор' : ''}}
                        </div>
                    </div>
                `;
            }}

            function renderShop() {{
                const section = document.getElementById('shop-section');
                fetch('/api/shop')
                    .then(res => res.json())
                    .then(data => {{
                        const categories = {{
                            rank: '⭐ Звания',
                            frame: '🖼 Рамки',
                            avatar: '🎨 Аватарки',
                            card: '🃏 Карты'
                        }};
                        
                        let html = `
                            <h2 style="margin-bottom: 20px;">🛒 Магазин</h2>
                            <p style="opacity: 0.6; margin-bottom: 20px;">Ваши баллы: <strong style="color: #f5576c;">${{currentUser ? currentUser.points || 0 : 0}} ПТ</strong></p>
                        `;

                        // Группируем по категориям
                        const grouped = {{}};
                        data.items.forEach(item => {{
                            if (!grouped[item.category]) grouped[item.category] = [];
                            grouped[item.category].push(item);
                        }});

                        for (const [category, items] of Object.entries(grouped)) {{
                            html += `<h3 style="margin: 20px 0 10px 0;">${{categories[category] || category}}</h3><div class="shop-grid">`;
                            items.forEach(item => {{
                                const owned = currentUser && currentUser.purchases && currentUser.purchases.some(p => p.item_id === item.id);
                                const isSelected = (category === 'avatar' && currentUser && currentUser.avatar === item.icon) ||
                                                  (category === 'frame' && currentUser && currentUser.frame_color === item.color) ||
                                                  (category === 'rank' && currentUser && currentUser.rank === item.name);
                                html += `
                                    <div class="shop-item">
                                        <div class="icon">${{item.icon}}</div>
                                        <div class="name">${{item.name}}</div>
                                        <div class="category-badge">${{category}}</div>
                                        <div class="price">${{item.price}} ПТ</div>
                                        ${{owned ? 
                                            (isSelected ? '<div class="selected-badge">✅ Выбрано</div>' : 
                                            `<button onclick="selectItem(${{item.id}}, '${{category}}')">Выбрать</button>`) : 
                                            `<button onclick="buyItem(${{item.id}})">Купить</button>`
                                        }}
                                    </div>
                                `;
                            }});
                            html += `</div>`;
                        }}
                        
                        section.innerHTML = html;
                    }});
            }}

            function buyItem(itemId) {{
                fetch('/api/buy', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ item_id: itemId }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        loadUserData();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function selectItem(itemId, category) {{
                fetch('/api/select_item', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ item_id: itemId, category: category }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        loadUserData();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function renderGames() {{
                const section = document.getElementById('games-section');
                section.innerHTML = `
                    <h2 style="margin-bottom: 20px;">🎮 Мини-игры</h2>
                    <p style="opacity: 0.6; margin-bottom: 20px;">Выберите игры и количество раундов, затем нажмите "Начать"</p>
                    <div class="game-container">
                        <div class="game-card">
                            <div class="game-icon">⚽</div>
                            <div class="game-name">Футбол</div>
                            <div class="game-checkbox">
                                <input type="checkbox" id="game_football" checked>
                                <label for="game_football">Включить</label>
                            </div>
                            <div class="game-count">
                                <input type="number" id="count_football" value="3" min="1" max="10">
                                <span>раундов</span>
                            </div>
                        </div>
                        <div class="game-card">
                            <div class="game-icon">🏀</div>
                            <div class="game-name">Баскетбол</div>
                            <div class="game-checkbox">
                                <input type="checkbox" id="game_basketball" checked>
                                <label for="game_basketball">Включить</label>
                            </div>
                            <div class="game-count">
                                <input type="number" id="count_basketball" value="3" min="1" max="10">
                                <span>раундов</span>
                            </div>
                        </div>
                        <div class="game-card">
                            <div class="game-icon">🎰</div>
                            <div class="game-name">Казино</div>
                            <div class="game-checkbox">
                                <input type="checkbox" id="game_casino" checked>
                                <label for="game_casino">Включить</label>
                            </div>
                            <div class="game-count">
                                <input type="number" id="count_casino" value="3" min="1" max="10">
                                <span>раундов</span>
                            </div>
                        </div>
                        <div class="game-card">
                            <div class="game-icon">🎯</div>
                            <div class="game-name">Дартс</div>
                            <div class="game-checkbox">
                                <input type="checkbox" id="game_darts" checked>
                                <label for="game_darts">Включить</label>
                            </div>
                            <div class="game-count">
                                <input type="number" id="count_darts" value="3" min="1" max="10">
                                <span>раундов</span>
                            </div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 20px;">
                        <button onclick="startGames()" style="padding: 15px 60px; font-size: 20px; background: rgba(245,87,108,0.3); border: 2px solid rgba(245,87,108,0.3); border-radius: 50px; color: white; cursor: pointer; transition: all 0.3s;">
                            🚀 Начать
                        </button>
                    </div>
                    <div id="gameResult" class="game-result"></div>
                `;
            }}

            function startGames() {{
                const games = [];
                const gameNames = ['football', 'basketball', 'casino', 'darts'];
                const gameIcons = ['⚽', '🏀', '🎰', '🎯'];
                const gameLabels = ['Футбол', 'Баскетбол', 'Казино', 'Дартс'];
                
                let totalGames = 0;
                let results = [];
                
                gameNames.forEach((name, index) => {{
                    const checkbox = document.getElementById('game_' + name);
                    const count = parseInt(document.getElementById('count_' + name).value);
                    if (checkbox && checkbox.checked) {{
                        for (let i = 0; i < count; i++) {{
                            games.push({{
                                id: name,
                                icon: gameIcons[index],
                                label: gameLabels[index]
                            }});
                            totalGames++;
                        }}
                    }}
                }});
                
                if (games.length === 0) {{
                    alert('Выберите хотя бы одну игру!');
                    return;
                }}
                
                // Анимация
                const resultDiv = document.getElementById('gameResult');
                resultDiv.className = 'game-result active';
                resultDiv.innerHTML = '<div style="text-align: center;"><p style="font-size: 24px;">🎮 Игры начались...</p><div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"></div></div>';
                
                let currentIndex = 0;
                const interval = setInterval(() => {{
                    if (currentIndex >= games.length) {{
                        clearInterval(interval);
                        finishGames(games);
                        return;
                    }}
                    const game = games[currentIndex];
                    const container = resultDiv.querySelector('div');
                    container.innerHTML += `<span style="font-size: 30px; animation: fadeIn 0.5s;">${{game.icon}}</span>`;
                    currentIndex++;
                }}, 300);
            }}

            function finishGames(games) {{
                // Симулируем результаты
                const results = games.map(game => {{
                    const score = Math.floor(Math.random() * 100) + 1;
                    return {{
                        ...game,
                        score: score,
                        win: score > 50
                    }};
                }});
                
                const wins = results.filter(r => r.win).length;
                const total = results.length;
                const winRate = total > 0 ? Math.round((wins / total) * 100) : 0;
                
                const resultDiv = document.getElementById('gameResult');
                resultDiv.innerHTML = `
                    <div style="text-align: center;">
                        <p style="font-size: 28px;">🏆 Результаты</p>
                        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin-top: 20px;">
                            ${{results.map(r => `
                                <div style="background: ${{r.win ? 'rgba(76, 205, 196, 0.2)' : 'rgba(255, 107, 107, 0.2)'}}; padding: 15px; border-radius: 10px; border: 1px solid ${{r.win ? '#4ecdc4' : '#ff6b6b'}};">
                                    <div style="font-size: 40px;">${{r.icon}}</div>
                                    <div style="font-weight: bold;">${{r.label}}</div>
                                    <div style="font-size: 24px;">${{r.score}}</div>
                                    <div>${{r.win ? '✅ Победа!' : '❌ Поражение'}}</div>
                                </div>
                            `).join('')}}
                        </div>
                        <div style="margin-top: 20px; padding: 20px; background: rgba(255,215,0,0.1); border-radius: 15px;">
                            <p style="font-size: 20px;">Всего игр: <strong>${{total}}</strong></p>
                            <p style="font-size: 20px;">Побед: <strong style="color: #4ecdc4;">${{wins}}</strong></p>
                            <p style="font-size: 20px;">Процент побед: <strong style="color: #ffe66d;">${{winRate}}%</strong></p>
                            <p style="font-size: 18px; margin-top: 10px; color: ${{winRate > 50 ? '#4ecdc4' : '#ff6b6b'}};">
                                ${{winRate > 50 ? '🔥 Отличный результат!' : '💪 Попробуй ещё раз!'}}
                            </p>
                        </div>
                        <button onclick="document.getElementById('gameResult').className='game-result'" style="margin-top: 20px; padding: 10px 30px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 50px; color: white; cursor: pointer;">
                            ✕ Закрыть
                        </button>
                    </div>
                `;
            }}

            function renderWins() {{
                const section = document.getElementById('wins-section');
                fetch('/api/wins')
                    .then(res => res.json())
                    .then(data => {{
                        const recentWins = data.wins.slice(-10).reverse();
                        const topWins = [...data.wins].sort((a, b) => b.amount - a.amount).slice(0, 10);

                        section.innerHTML = `
                            <h2 style="margin-bottom: 20px;">🎰 Розыгрыши</h2>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                                <div>
                                    <h3 style="margin-bottom: 15px;">📋 Недавние выигрыши</h3>
                                    <div class="wins-list">
                                        ${{recentWins.length === 0 ? '<p style="opacity: 0.3;">Пока нет выигрышей</p>' : recentWins.map(win => `
                                            <div class="win-item">
                                                <div>
                                                    <span class="telegram" onclick="viewUser('${{win.telegram}}')">${{win.telegram}}</span>
                                                    <span class="prize"> - ${{win.prize}}</span>
                                                </div>
                                                <div>
                                                    <span class="amount">+${{win.amount}} ПТ</span>
                                                    <span class="date">${{new Date(win.date).toLocaleDateString()}}</span>
                                                </div>
                                            </div>
                                        `).join('')}}
                                    </div>
                                </div>
                                <div>
                                    <h3 style="margin-bottom: 15px;">🏆 Топ по сумме ПТ</h3>
                                    <div class="wins-list">
                                        ${{topWins.length === 0 ? '<p style="opacity: 0.3;">Нет данных</p>' : topWins.map((win, index) => `
                                            <div class="win-item">
                                                <div>
                                                    <span style="opacity: 0.5;">${{index + 1}}.</span>
                                                    <span class="telegram" onclick="viewUser('${{win.telegram}}')">${{win.telegram}}</span>
                                                </div>
                                                <div>
                                                    <span class="amount">${{win.amount}} ПТ</span>
                                                </div>
                                            </div>
                                        `).join('')}}
                                    </div>
                                </div>
                            </div>
                        `;
                    }});
            }}

            function renderTop() {{
                const section = document.getElementById('top-section');
                fetch('/api/top')
                    .then(res => res.json())
                    .then(data => {{
                        section.innerHTML = `
                            <h2 style="margin-bottom: 20px;">🏆 Топ участников</h2>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                                <div>
                                    <h3 style="margin-bottom: 15px;">💰 Топ по ПТ</h3>
                                    <div class="wins-list">
                                        ${{data.by_points.length === 0 ? '<p style="opacity: 0.3;">Нет данных</p>' : data.by_points.map((user, index) => `
                                            <div class="win-item">
                                                <div>
                                                    <span style="opacity: 0.5;">${{index + 1}}.</span>
                                                    <span onclick="viewUser('${{user.telegram}}')" style="cursor:pointer; font-weight:bold; color: #ffe66d;">${{user.name}} ${{user.is_admin ? '👑' : ''}}</span>
                                                    <span style="opacity:0.5;">${{user.telegram}}</span>
                                                </div>
                                                <div>
                                                    <span style="color: #f5576c; font-weight:bold;">${{user.points}} ПТ</span>
                                                    ${{user.rank ? `<span style="margin-left:10px;">⭐ ${{user.rank}}</span>` : ''}}
                                                </div>
                                            </div>
                                        `).join('')}}
                                    </div>
                                </div>
                                <div>
                                    <h3 style="margin-bottom: 15px;">🏆 Топ по победам</h3>
                                    <div class="wins-list">
                                        ${{data.by_wins.length === 0 ? '<p style="opacity: 0.3;">Нет данных</p>' : data.by_wins.map((user, index) => `
                                            <div class="win-item">
                                                <div>
                                                    <span style="opacity: 0.5;">${{index + 1}}.</span>
                                                    <span onclick="viewUser('${{user.telegram}}')" style="cursor:pointer; font-weight:bold; color: #4ecdc4;">${{user.name}} ${{user.is_admin ? '👑' : ''}}</span>
                                                    <span style="opacity:0.5;">${{user.telegram}}</span>
                                                </div>
                                                <div>
                                                    <span style="color: #4ecdc4; font-weight:bold;">${{user.wins}} 🏆</span>
                                                    ${{user.rank ? `<span style="margin-left:10px;">⭐ ${{user.rank}}</span>` : ''}}
                                                </div>
                                            </div>
                                        `).join('')}}
                                    </div>
                                </div>
                            </div>
                        `;
                    }});
            }}

            function renderCompetitions() {{
                const section = document.getElementById('competitions-section');
                fetch('/api/competitions')
                    .then(res => res.json())
                    .then(data => {{
                        if (!data.competitions || data.competitions.length === 0) {{
                            section.innerHTML = `
                                <h2 style="margin-bottom: 20px;">🏆 Соревнования</h2>
                                <p style="opacity: 0.3; text-align: center; padding: 40px;">Активных соревнований нет</p>
                            `;
                            return;
                        }}
                        
                        let html = `<h2 style="margin-bottom: 20px;">🏆 Активные соревнования</h2>`;
                        
                        data.competitions.forEach(comp => {{
                            const isFinished = comp.status === 'finished';
                            html += `
                                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                                    <h3>${{comp.name}} ${{isFinished ? '✅ Завершено' : '🟢 Активно'}}</h3>
                                    <p style="opacity: 0.6;">Игры: ${{comp.games.join(', ')}}</p>
                                    <p style="opacity: 0.6;">Очков за победу: ${{comp.points_per_win}}</p>
                                    <p style="opacity: 0.6;">Приз: ${{comp.prize || 'Нет'}} (${{comp.prize_type}})</p>
                                    ${{isFinished ? `
                                        <div style="margin-top: 10px; background: rgba(255,215,0,0.1); padding: 10px; border-radius: 10px;">
                                            <p style="color: #ffe66d;">🏆 Результаты:</p>
                                            ${{Object.entries(comp.results || {{}}).map(([telegram, wins]) => `
                                                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                                    <span onclick="viewUser('${{telegram}}')" style="cursor:pointer; color: #4ecdc4;">${{telegram}}</span>
                                                    <span>${{wins}} побед</span>
                                                </div>
                                            `).join('')}}
                                        </div>
                                    ` : `
                                        <div style="margin-top: 10px; display: flex; gap: 10px;">
                                            <input type="number" id="result_${{comp.id}}" placeholder="Ваши победы">
                                            <button onclick="submitResult(${{comp.id}})" style="padding: 8px 20px; background: rgba(76, 205, 196, 0.3); border: 1px solid rgba(76, 205, 196, 0.3); border-radius: 10px; color: white; cursor: pointer;">Отправить результат</button>
                                        </div>
                                    `}}
                                </div>
                            `;
                        }});
                        
                        section.innerHTML = html;
                    }});
            }}

            function submitResult(compId) {{
                const wins = document.getElementById('result_' + compId).value;
                if (!wins || wins <= 0) {{
                    alert('Введите количество побед!');
                    return;
                }}
                
                fetch('/api/competition/result', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ comp_id: compId, wins: parseInt(wins) }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        renderCompetitions();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function viewUser(telegram) {{
                fetch('/api/user_by_telegram', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ telegram: telegram }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        const user = data.user;
                        const modal = document.getElementById('userProfileModal');
                        document.getElementById('userProfileContent').innerHTML = `
                            <div style="text-align: center;">
                                <div class="profile-frame" style="border-color: ${{user.frame_color || '#f5576c'}}">
                                    <div class="profile-avatar">${{user.avatar || '👤'}}</div>
                                </div>
                                ${{user.rank ? `<div class="profile-rank">${{user.rank}}</div>` : ''}}
                                <h2 style="font-size: 28px; margin: 10px 0;">
                                    ${{user.name}}
                                    ${{user.is_admin ? '<span class="admin-crown">👑</span>' : ''}}
                                </h2>
                                <p style="opacity: 0.6; margin-bottom: 20px;">${{user.telegram}}</p>
                                <div class="profile-info">
                                    <div class="profile-card">
                                        <div class="value" style="color: #f5576c;">${{user.points || 0}}</div>
                                        <div class="label">💰 ПТ Баллов</div>
                                    </div>
                                    <div class="profile-card">
                                        <div class="value" style="color: #4ecdc4;">${{user.wins_count || 0}}</div>
                                        <div class="label">🏆 Побед</div>
                                    </div>
                                    <div class="profile-card">
                                        <div class="value" style="color: #ffe66d; font-size: 20px;">${{user.rank || 'Нет звания'}}</div>
                                        <div class="label">⭐ Звание</div>
                                    </div>
                                </div>
                                ${{user.is_admin ? '<div style="margin-top:15px; color: #ffd700; font-size:18px;">👑 Администратор</div>' : ''}}
                            </div>
                        `;
                        modal.classList.add('active');
                    }}
                }});
            }}

            function closeUserProfile() {{
                document.getElementById('userProfileModal').classList.remove('active');
            }}

            // === АДМИН ФУНКЦИИ ===

            function showAdminPanel() {{
                document.getElementById('adminModal').classList.add('active');
                document.getElementById('adminContent').style.display = 'none';
                document.getElementById('adminCode').value = '';
            }}

            function closeAdminPanel() {{
                document.getElementById('adminModal').classList.remove('active');
            }}

            function checkAdminCode() {{
                const code = document.getElementById('adminCode').value;
                currentAdminCode = code;
                
                fetch('/api/admin/check', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ code: code }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        document.getElementById('adminContent').style.display = 'block';
                        loadUsersList();
                        loadAdminShop();
                        loadAdminWins();
                        loadAdminCompetitions();
                    }} else {{
                        alert('❌ Неверный код доступа!');
                    }}
                }});
            }}

            function loadUsersList() {{
                fetch('/api/admin/users')
                    .then(res => res.json())
                    .then(data => {{
                        if (!data.success) {{
                            document.getElementById('usersList').innerHTML = '<p style="opacity:0.5;">Нет прав или ошибка</p>';
                            return;
                        }}
                        const list = document.getElementById('usersList');
                        list.innerHTML = `
                            <div class="users-grid">
                                ${{data.users.map(user => `
                                    <div class="user-card" onclick="viewUser('${{user.telegram}}')">
                                        <div class="user-info">
                                            <span class="user-name">${{user.avatar || '👤'}} ${{user.name}} ${{user.is_admin ? '👑' : ''}}</span>
                                            <span class="user-telegram">${{user.telegram}}</span>
                                            <span class="user-stats">${{user.points}} ПТ • ${{user.wins}} побед ${{user.rank ? '• ⭐ ' + user.rank : ''}}</span>
                                        </div>
                                        <div>
                                            ${{user.is_admin ? '<span class="admin-badge">👑 Админ</span>' : 
                                            `<button class="make-admin-btn" onclick="event.stopPropagation(); makeAdmin('${{user.id}}')">Назначить админом</button>`}}
                                        </div>
                                    </div>
                                `).join('')}}
                            </div>
                        `;
                    }});
            }}

            function makeAdmin(userId) {{
                if (!confirm('Назначить этого пользователя администратором?')) return;
                
                fetch('/api/admin/make_admin', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ 
                        user_id: userId,
                        code: currentAdminCode 
                    }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        loadUsersList();
                        loadUserData();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function changeCode() {{
                const oldCode = document.getElementById('oldCode').value;
                const newCode = document.getElementById('newCode').value;
                
                if (!oldCode || !newCode) {{
                    alert('Заполните оба поля!');
                    return;
                }}
                
                if (newCode.length < 4) {{
                    alert('Новый код должен быть минимум 4 символа');
                    return;
                }}
                
                fetch('/api/admin/change_code', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ 
                        old_code: oldCode,
                        new_code: newCode 
                    }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        document.getElementById('oldCode').value = '';
                        document.getElementById('newCode').value = '';
                        currentAdminCode = newCode;
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function loadAdminShop() {{
                fetch('/api/shop')
                    .then(res => res.json())
                    .then(data => {{
                        const list = document.getElementById('shopItemsList');
                        list.innerHTML = data.items.map(item => `
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <span>${{item.icon}} ${{item.name}} - ${{item.price}} ПТ (${{item.category}})${{item.color ? ' Цвет: ' + item.color : ''}}</span>
                                <button onclick="deleteShopItem(${{item.id}})" style="background: rgba(255,0,0,0.2); border: none; color: white; padding: 5px 15px; border-radius: 5px; cursor: pointer;">🗑</button>
                            </div>
                        `).join('');
                    }});
            }}

            function addShopItem() {{
                const name = document.getElementById('itemName').value;
                const price = parseInt(document.getElementById('itemPrice').value);
                const category = document.getElementById('itemCategory').value;
                const icon = document.getElementById('itemIcon').value;
                const color = document.getElementById('itemColor').value;

                if (!name || !price || !icon) {{
                    alert('Заполните все поля!');
                    return;
                }}

                fetch('/api/admin/shop/add', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name, price, category, icon, color: color || null }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ Товар добавлен!');
                        document.getElementById('itemName').value = '';
                        document.getElementById('itemPrice').value = '';
                        document.getElementById('itemIcon').value = '';
                        document.getElementById('itemColor').value = '';
                        loadAdminShop();
                        renderShop();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function deleteShopItem(itemId) {{
                if (!confirm('Удалить товар?')) return;
                fetch('/api/admin/shop/delete', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ item_id: itemId }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ Товар удален!');
                        loadAdminShop();
                        renderShop();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function loadAdminWins() {{
                fetch('/api/wins')
                    .then(res => res.json())
                    .then(data => {{
                        const list = document.getElementById('winsListAdmin');
                        list.innerHTML = data.wins.slice().reverse().slice(0, 20).map(win => `
                            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <span>${{win.telegram}} - ${{win.prize}} (+${{win.amount}} ПТ)</span>
                                <button onclick="deleteWin(${{win.id}})" style="background: rgba(255,0,0,0.2); border: none; color: white; padding: 5px 15px; border-radius: 5px; cursor: pointer;">🗑</button>
                            </div>
                        `).join('');
                    }});
            }}

            function addWinAdmin() {{
                const telegram = document.getElementById('winTelegram').value;
                const prize = document.getElementById('winPrize').value;
                const amount = parseInt(document.getElementById('winAmount').value);

                if (!telegram || !prize || !amount) {{
                    alert('Заполните все поля!');
                    return;
                }}

                fetch('/api/admin/win/add', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ telegram, prize, amount }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ Выигрыш добавлен!');
                        document.getElementById('winTelegram').value = '';
                        document.getElementById('winPrize').value = '';
                        document.getElementById('winAmount').value = '';
                        loadAdminWins();
                        renderWins();
                        loadUserData();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function deleteWin(winId) {{
                if (!confirm('Удалить выигрыш?')) return;
                fetch('/api/admin/win/delete', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ win_id: winId }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ Выигрыш удален!');
                        loadAdminWins();
                        renderWins();
                        loadUserData();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            // === УПРАВЛЕНИЕ СОРЕВНОВАНИЯМИ ===

            function loadAdminCompetitions() {{
                fetch('/api/competitions')
                    .then(res => res.json())
                    .then(data => {{
                        const list = document.getElementById('competitionsListAdmin');
                        if (!data.competitions || data.competitions.length === 0) {{
                            list.innerHTML = '<p style="opacity:0.5;">Нет соревнований</p>';
                            return;
                        }}
                        list.innerHTML = data.competitions.map(comp => `
                            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong>${{comp.name}}</strong>
                                        <span style="margin-left: 10px; font-size: 12px; opacity: 0.5;">(${{comp.status}})</span>
                                        <div style="font-size: 12px; opacity: 0.5;">Игры: ${{comp.games.join(', ')}}</div>
                                        <div style="font-size: 12px; opacity: 0.5;">Приз: ${{comp.prize || 'Нет'}} (${{comp.prize_type}})</div>
                                    </div>
                                    <div>
                                        <button onclick="finishCompetition(${{comp.id}})" style="background: rgba(76, 205, 196, 0.3); border: 1px solid rgba(76, 205, 196, 0.3); border-radius: 10px; color: white; padding: 5px 15px; cursor: pointer;">Завершить</button>
                                        <button onclick="deleteCompetition(${{comp.id}})" style="background: rgba(255,0,0,0.2); border: 1px solid rgba(255,0,0,0.2); border-radius: 10px; color: white; padding: 5px 15px; cursor: pointer;">🗑</button>
                                    </div>
                                </div>
                            </div>
                        `).join('');
                    }});
            }}

            function createCompetition() {{
                const name = document.getElementById('compName').value;
                const points_per_win = parseInt(document.getElementById('compPoints').value);
                const games_str = document.getElementById('compGames').value;
                const prize = document.getElementById('compPrize').value;
                const prize_value = parseInt(document.getElementById('compPrizeValue').value);
                const prize_type = document.getElementById('compPrizeType').value;

                if (!name || !games_str) {{
                    alert('Заполните название и игры!');
                    return;
                }}

                const games = games_str.split(',').map(g => g.trim()).filter(g => g);

                fetch('/api/admin/competition/create', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name, games, points_per_win, prize, prize_value, prize_type }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        document.getElementById('compName').value = '';
                        document.getElementById('compGames').value = '';
                        document.getElementById('compPrize').value = '';
                        document.getElementById('compPrizeValue').value = '0';
                        loadAdminCompetitions();
                        renderCompetitions();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function finishCompetition(compId) {{
                const results_str = prompt('Введите результаты в формате: @telegram1:победы, @telegram2:победы\\nНапример: @Ale7xey:5, @Test:3');
                if (!results_str) return;
                
                const results = {{}};
                results_str.split(',').forEach(item => {{
                    const parts = item.trim().split(':');
                    if (parts.length === 2) {{
                        results[parts[0].trim()] = parseInt(parts[1].trim());
                    }}
                }});
                
                fetch('/api/admin/competition/finish', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ comp_id: compId, results: results }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        loadAdminCompetitions();
                        renderCompetitions();
                        loadUserData();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function deleteCompetition(compId) {{
                if (!confirm('Удалить соревнование?')) return;
                fetch('/api/admin/competition/delete', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ comp_id: compId }})
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.success) {{
                        alert('✅ ' + data.message);
                        loadAdminCompetitions();
                        renderCompetitions();
                    }} else {{
                        alert('❌ ' + data.message);
                    }}
                }});
            }}

            function logout() {{
                fetch('/logout')
                    .then(() => window.location.href = '/');
            }}

            loadUserData();
            showSection('profile');
        </script>
    </body>
    </html>
    '''

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
            'id': session['user_id'],
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
            'purchases': user.get('purchases', []),
            'is_admin': user.get('is_admin', False)
        }
    })

@app.route('/api/change_avatar', methods=['POST'])
@login_required
def api_change_avatar():
    data = request.get_json()
    new_avatar = data.get('avatar', '').strip()
    
    if not new_avatar:
        return jsonify({'success': False, 'message': 'Аватарка не выбрана'})
    
    users = load_users()
    user = users.get(session['user_id'])
    
    purchased = user.get('purchases', [])
    avatar_items = [p for p in purchased if p.get('category') == 'avatar' and p.get('icon') == new_avatar]
    
    if not avatar_items:
        return jsonify({'success': False, 'message': 'У вас нет этой аватарки'})
    
    user['avatar'] = new_avatar
    save_users(users)
    return jsonify({'success': True, 'message': 'Аватарка изменена!'})

@app.route('/api/select_item', methods=['POST'])
@login_required
def api_select_item():
    data = request.get_json()
    item_id = data.get('item_id')
    category = data.get('category')
    
    users = load_users()
    user = users.get(session['user_id'])
    
    # Проверяем что предмет куплен
    purchased = user.get('purchases', [])
    item = next((p for p in purchased if p.get('item_id') == item_id), None)
    if not item:
        return jsonify({'success': False, 'message': 'У вас нет этого предмета'})
    
    shop = load_shop()
    shop_item = next((i for i in shop['items'] if i['id'] == item_id), None)
    if not shop_item:
        return jsonify({'success': False, 'message': 'Предмет не найден'})
    
    if category == 'avatar':
        user['avatar'] = shop_item['icon']
    elif category == 'frame':
        user['frame'] = shop_item['icon']
        user['frame_color'] = shop_item.get('color', '#f5576c')
    elif category == 'rank':
        user['rank'] = shop_item['name']
    
    save_users(users)
    return jsonify({'success': True, 'message': f'{shop_item["name"]} выбрано!'})

@app.route('/api/top')
def api_top():
    users = load_users()
    wins = load_wins()
    
    user_data = []
    for uid, user in users.items():
        user_wins = [w for w in wins['wins'] if w['telegram'] == user['telegram']]
        user_data.append({
            'id': uid,
            'name': user.get('name', ''),
            'telegram': user.get('telegram', ''),
            'points': user.get('points', 0),
            'wins': len(user_wins),
            'rank': user.get('rank', ''),
            'avatar': user.get('avatar', '👤'),
            'is_admin': user.get('is_admin', False)
        })
    
    by_points = sorted(user_data, key=lambda x: x['points'], reverse=True)[:20]
    by_wins = sorted(user_data, key=lambda x: x['wins'], reverse=True)[:20]
    
    return jsonify({
        'success': True,
        'by_points': by_points,
        'by_wins': by_wins
    })

@app.route('/api/user_by_telegram', methods=['POST'])
def api_user_by_telegram():
    data = request.get_json()
    telegram = data.get('telegram', '').strip()
    
    users = load_users()
    user = None
    user_id = None
    
    for uid, u in users.items():
        if u.get('telegram') == telegram:
            user = u
            user_id = uid
            break
    
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})
    
    wins = load_wins()
    user_wins = [w for w in wins['wins'] if w['telegram'] == user['telegram']]
    
    return jsonify({
        'success': True,
        'user': {
            'name': user['name'],
            'telegram': user['telegram'],
            'points': user.get('points', 0),
            'wins_count': len(user_wins),
            'rank': user.get('rank', ''),
            'frame': user.get('frame', '🖼'),
            'frame_color': user.get('frame_color', '#f5576c'),
            'avatar': user.get('avatar', '👤'),
            'is_admin': user.get('is_admin', False)
        }
    })

# === API СОРЕВНОВАНИЙ ===

@app.route('/api/competitions')
def api_competitions():
    comps = load_competitions()
    active = [c for c in comps['competitions'] if c.get('status') in ['active', 'finished']]
    return jsonify({'success': True, 'competitions': active})

@app.route('/api/competition/result', methods=['POST'])
@login_required
def api_competition_result():
    data = request.get_json()
    comp_id = data.get('comp_id')
    wins = data.get('wins', 0)
    
    if wins <= 0:
        return jsonify({'success': False, 'message': 'Введите количество побед'})
    
    comps = load_competitions()
    comp = next((c for c in comps['competitions'] if c['id'] == comp_id), None)
    if not comp:
        return jsonify({'success': False, 'message': 'Соревнование не найдено'})
    
    if comp['status'] != 'active':
        return jsonify({'success': False, 'message': 'Соревнование уже завершено'})
    
    users = load_users()
    user = users.get(session['user_id'])
    telegram = user.get('telegram')
    
    if 'results' not in comp:
        comp['results'] = {}
    
    comp['results'][telegram] = comp['results'].get(telegram, 0) + wins
    save_competitions(comps)
    
    return jsonify({'success': True, 'message': f'Результат добавлен! Всего побед: {comp["results"][telegram]}'})

@app.route('/api/admin/competition/create', methods=['POST'])
@admin_required
def admin_create_competition():
    data = request.get_json()
    
    name = data.get('name', '').strip()
    games = data.get('games', [])
    points_per_win = data.get('points_per_win', 10)
    prize = data.get('prize', '')
    prize_value = data.get('prize_value', 0)
    prize_type = data.get('prize_type', 'points')
    
    if not name or not games:
        return jsonify({'success': False, 'message': 'Название и игры обязательны'})
    
    comps = load_competitions()
    comps['last_id'] += 1
    
    comp = {
        'id': comps['last_id'],
        'name': name,
        'games': games,
        'points_per_win': points_per_win,
        'prize': prize,
        'prize_value': prize_value,
        'prize_type': prize_type,
        'status': 'active',
        'results': {},
        'created_at': datetime.now().isoformat(),
        'created_by': session.get('user_name', 'admin')
    }
    
    comps['competitions'].append(comp)
    save_competitions(comps)
    
    return jsonify({'success': True, 'message': f'Соревнование "{name}" создано!', 'competition': comp})

@app.route('/api/admin/competition/finish', methods=['POST'])
@admin_required
def admin_finish_competition():
    data = request.get_json()
    comp_id = data.get('comp_id')
    results = data.get('results', {})
    
    comps = load_competitions()
    comp = next((c for c in comps['competitions'] if c['id'] == comp_id), None)
    if not comp:
        return jsonify({'success': False, 'message': 'Соревнование не найдено'})
    
    comp['status'] = 'finished'
    comp['results'] = results
    comp['finished_at'] = datetime.now().isoformat()
    save_competitions(comps)
    
    users = load_users()
    winner_telegram = max(results, key=results.get) if results else None
    
    if winner_telegram:
        for user_id, user in users.items():
            if user['telegram'] == winner_telegram:
                if comp['prize_type'] == 'points':
                    user['points'] = user.get('points', 0) + comp['prize_value']
                elif comp['prize_type'] == 'rank':
                    user['rank'] = comp['prize']
                elif comp['prize_type'] == 'frame':
                    user['frame'] = comp['prize']
                    user['frame_color'] = '#ffd700'
                elif comp['prize_type'] == 'avatar':
                    user['avatar'] = comp['prize']
                
                if 'competition_wins' not in user:
                    user['competition_wins'] = []
                user['competition_wins'].append({
                    'comp_id': comp_id,
                    'comp_name': comp['name'],
                    'wins': results.get(winner_telegram, 0),
                    'date': datetime.now().isoformat()
                })
                
                save_users(users)
                break
    
    return jsonify({'success': True, 'message': f'Соревнование "{comp["name"]}" завершено! Победитель: {winner_telegram}'})

@app.route('/api/admin/competition/delete', methods=['POST'])
@admin_required
def admin_delete_competition():
    data = request.get_json()
    comp_id = data.get('comp_id')
    
    comps = load_competitions()
    comps['competitions'] = [c for c in comps['competitions'] if c['id'] != comp_id]
    save_competitions(comps)
    
    return jsonify({'success': True, 'message': 'Соревнование удалено'})

# === ОСТАЛЬНЫЕ API ===

@app.route('/api/admin/check', methods=['POST'])
def admin_check():
    data = request.get_json()
    code = data.get('code', '').strip()
    
    if code == get_admin_code():
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/users')
@login_required
def admin_get_users():
    users = load_users()
    current_user = users.get(session['user_id'])
    if not current_user or not current_user.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Нет прав'}), 403
    
    wins = load_wins()
    user_list = []
    for uid, user in users.items():
        user_wins = [w for w in wins['wins'] if w['telegram'] == user['telegram']]
        user_list.append({
            'id': uid,
            'name': user.get('name', ''),
            'telegram': user.get('telegram', ''),
            'points': user.get('points', 0),
            'wins': len(user_wins),
            'is_admin': user.get('is_admin', False),
            'rank': user.get('rank', ''),
            'avatar': user.get('avatar', '👤'),
            'registered_at': user.get('registered_at', '')
        })
    
    return jsonify({'success': True, 'users': user_list})

@app.route('/api/admin/make_admin', methods=['POST'])
@login_required
def admin_make_admin():
    data = request.get_json()
    user_id = data.get('user_id')
    code = data.get('code', '').strip()
    
    if code != get_admin_code():
        return jsonify({'success': False, 'message': 'Неверный код!'})
    
    users = load_users()
    current_user = users.get(session['user_id'])
    if not current_user or not current_user.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Нет прав'}), 403
    
    if user_id not in users:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})
    
    users[user_id]['is_admin'] = True
    save_users(users)
    
    return jsonify({'success': True, 'message': 'Пользователь назначен администратором!'})

@app.route('/api/admin/change_code', methods=['POST'])
@login_required
def admin_change_code():
    data = request.get_json()
    old_code = data.get('old_code', '').strip()
    new_code = data.get('new_code', '').strip()
    
    users = load_users()
    current_user = users.get(session['user_id'])
    if not current_user or not current_user.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Нет прав'}), 403
    
    if old_code != get_admin_code():
        return jsonify({'success': False, 'message': 'Неверный старый код!'})
    
    if len(new_code) < 4:
        return jsonify({'success': False, 'message': 'Новый код должен быть минимум 4 символа'})
    
    with open(get_file_path('admin_code.txt'), 'w') as f:
        f.write(new_code)
    
    return jsonify({'success': True, 'message': 'Код успешно изменен!'})

@app.route('/api/admin/shop/add', methods=['POST'])
@admin_required
def admin_add_shop():
    data = request.get_json()
    shop = load_shop()
    
    new_id = max([i['id'] for i in shop['items']]) + 1 if shop['items'] else 1
    shop['items'].append({
        'id': new_id,
        'name': data['name'],
        'price': data['price'],
        'category': data['category'],
        'icon': data['icon'],
        'color': data.get('color')
    })
    save_shop(shop)
    return jsonify({'success': True, 'message': 'Товар добавлен'})

@app.route('/api/admin/shop/delete', methods=['POST'])
@admin_required
def admin_delete_shop():
    data = request.get_json()
    shop = load_shop()
    shop['items'] = [i for i in shop['items'] if i['id'] != data['item_id']]
    save_shop(shop)
    return jsonify({'success': True, 'message': 'Товар удален'})

@app.route('/api/admin/win/add', methods=['POST'])
@admin_required
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
@admin_required
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
        'icon': item['icon'],
        'color': item.get('color'),
        'date': datetime.now().isoformat()
    })
    
    if item['category'] == 'rank':
        user['rank'] = item['name']
    elif item['category'] == 'frame':
        user['frame'] = item['icon']
        user['frame_color'] = item.get('color', '#f5576c')
    elif item['category'] == 'avatar':
        pass
    elif item['category'] == 'card':
        pass
    
    save_users(users)
    return jsonify({'success': True, 'message': f'Вы купили {item["name"]}!'})

@app.route('/api/wins')
def api_wins():
    wins = load_wins()
    return jsonify(wins)

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
        
        is_admin = (telegram == '@Ale7xey')
        
        users[user_id] = {
            'name': name,
            'telegram': telegram,
            'password_hash': hash_password(password),
            'ip': client_ip,
            'points': 0,
            'registered_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'purchases': [],
            'rank': '',
            'frame': '🖼',
            'frame_color': '#f5576c',
            'avatar': '👤',
            'is_admin': is_admin
        }
        
        save_users(users)
        session['user_id'] = user_id
        session['user_name'] = name
        
        admin_msg = " Вы назначены администратором!" if is_admin else ""
        
        return jsonify({
            'success': True,
            'message': f'Добро пожаловать, {name}!{admin_msg}',
            'redirect': '/app'
        })
        
    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return jsonify({'success': False, 'message': 'Ошибка на сервере'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    telegram = data.get('telegram', '').strip()
    password = data.get('password', '')
    
    users = load_users()
    
    for user_id, user in users.items():
        if user.get('telegram') == telegram:
            if user.get('password_hash') == hash_password(password):
                if telegram == '@Ale7xey' and not user.get('is_admin', False):
                    user['is_admin'] = True
                    save_users(users)
                    print("✅ @Ale7xey назначен админом при входе!")
                
                session['user_id'] = user_id
                session['user_name'] = user.get('name')
                return jsonify({'success': True, 'message': 'Добро пожаловать!'})
            else:
                return jsonify({'success': False, 'message': 'Неверный пароль!'})
    
    return jsonify({'success': False, 'message': 'Пользователь не найден!'})

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

# === СБРОС ПРИЛОЖЕНИЯ ===
@app.route('/reset')
def reset_app():
    key = request.args.get('key', '')
    if key != 'reset123':
        return "❌ Неверный ключ! Используй ?key=reset123", 403
    
    users = {}
    save_users(users)
    
    wins = {'wins': [], 'last_id': 0}
    save_wins(wins)
    
    shop = {
        'items': [
            {'id': 1, 'name': '👑 Победитель', 'price': 500, 'category': 'rank', 'icon': '👑', 'color': '#ffe66d'},
            {'id': 2, 'name': '⭐ Чемпион', 'price': 1000, 'category': 'rank', 'icon': '⭐', 'color': '#ffd700'},
            {'id': 3, 'name': '🎖 Легенда', 'price': 2000, 'category': 'rank', 'icon': '🎖', 'color': '#ff6b6b'},
            {'id': 4, 'name': '🖼 Золотая рамка', 'price': 300, 'category': 'frame', 'icon': '🖼', 'color': '#ffd700'},
            {'id': 5, 'name': '🖼 Серебряная рамка', 'price': 200, 'category': 'frame', 'icon': '🖼', 'color': '#c0c0c0'},
            {'id': 6, 'name': '🖼 Бронзовая рамка', 'price': 100, 'category': 'frame', 'icon': '🖼', 'color': '#cd7f32'},
            {'id': 7, 'name': '💎 Алмазная рамка', 'price': 500, 'category': 'frame', 'icon': '💎', 'color': '#00ffff'},
            {'id': 8, 'name': '🐱 Аватарка Кот', 'price': 150, 'category': 'avatar', 'icon': '🐱', 'color': None},
            {'id': 9, 'name': '🐶 Аватарка Пёс', 'price': 150, 'category': 'avatar', 'icon': '🐶', 'color': None},
            {'id': 10, 'name': '🦊 Аватарка Лиса', 'price': 150, 'category': 'avatar', 'icon': '🦊', 'color': None},
            {'id': 11, 'name': '🐲 Аватарка Дракон', 'price': 300, 'category': 'avatar', 'icon': '🐲', 'color': None},
            {'id': 12, 'name': '🌈 Аватарка Радуга', 'price': 200, 'category': 'avatar', 'icon': '🌈', 'color': None},
        ]
    }
    save_shop(shop)
    
    comps = {'competitions': [], 'last_id': 0}
    save_competitions(comps)
    
    with open(get_file_path('admin_code.txt'), 'w') as f:
        f.write('132547')
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Обнуление</title>
        <style>
            body { 
                font-family: Arial; 
                text-align: center; 
                padding: 50px; 
                background: #1a1a2e; 
                color: white;
            }
            .success { color: #4ecdc4; font-size: 24px; }
            .btn { 
                display: inline-block; 
                padding: 15px 40px; 
                background: #f5576c; 
                color: white; 
                text-decoration: none; 
                border-radius: 10px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="success">✅ Приложение обнулено!</div>
        <p>Все пользователи и выигрыши удалены.</p>
        <p>Магазин восстановлен до стандартного.</p>
        <a href="/" class="btn">На главную</a>
    </body>
    </html>
    """

# === ЗАПУСК ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
