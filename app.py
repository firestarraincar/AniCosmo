from flask import Flask, send_file, request, jsonify, session
import os
import json
import hashlib
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Обязательно изменить!

# Файл для хранения пользователей
USERS_FILE = 'users.json'

# Функция для загрузки пользователей
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Функция для сохранения пользователей
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Хеширование пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Проверка IP (защита от множественных регистраций)
def get_client_ip():
    # Для реального IP через прокси
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AniCosmo</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

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

            /* === ЭКРАН 1: Главный === */
            #screen-main {
                position: relative;
                z-index: 10;
                text-align: center;
                transition: opacity 0.8s, transform 0.8s;
                padding: 20px;
            }

            #screen-main h1 {
                font-size: 52px;
                font-weight: 700;
                letter-spacing: 2px;
                text-shadow: 0 0 60px rgba(0,0,0,0.8);
                margin-bottom: 25px;
            }

            #screen-main .channel-block {
                margin-bottom: 45px;
            }

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
                text-shadow: 0 0 30px rgba(255, 107, 107, 0.2);
            }

            #screen-main .channel-block a:hover {
                color: #ff8a8a;
            }

            #screen-main .btn-start {
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

            #screen-main .btn-start:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.5);
                transform: scale(1.03);
                box-shadow: 0 0 40px rgba(255, 255, 255, 0.05);
            }

            /* === ЭКРАН 2: Регистрация === */
            #screen-register {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.8s;
                padding: 40px;
                z-index: 10;
            }

            #screen-register.active {
                opacity: 1;
                pointer-events: auto;
            }

            .register-box {
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(20px);
                padding: 50px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                max-width: 450px;
                width: 100%;
                text-align: center;
                box-shadow: 0 30px 60px rgba(0,0,0,0.5);
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

            .ip-info {
                margin-top: 20px;
                font-size: 12px;
                opacity: 0.3;
                letter-spacing: 1px;
            }

            /* Анимация для предупреждения */
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

        <!-- ЭКРАН 1: Главный -->
        <div id="screen-main">
            <h1>AniCosmo — канал по Аникарду</h1>
            <div class="channel-block">
                <div class="label">Канал</div>
                <a href="https://t.me/AniCosmoDay" target="_blank">@AniCosmoDay</a>
            </div>
            <button class="btn-start" onclick="goToRegister()">Начать</button>
        </div>

        <!-- ЭКРАН 2: Регистрация -->
        <div id="screen-register">
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
                <button class="btn-back" onclick="goBack()">← Назад</button>
                <div class="ip-info" id="ipDisplay">Загрузка IP...</div>
            </div>
        </div>

        <div class="footer">ANICOSMO</div>

        <script>
            // Переход на регистрацию
            function goToRegister() {
                const main = document.getElementById('screen-main');
                main.style.opacity = '0';
                main.style.transform = 'scale(0.95)';

                setTimeout(() => {
                    main.style.display = 'none';
                    document.getElementById('screen-register').classList.add('active');
                    // Показываем IP
                    fetch('/get_ip')
                        .then(res => res.json())
                        .then(data => {
                            document.getElementById('ipDisplay').textContent = 'IP: ' + data.ip;
                        })
                        .catch(() => {
                            document.getElementById('ipDisplay').textContent = 'IP: Не удалось определить';
                        });
                }, 800);
            }

            // Назад на главный экран
            function goBack() {
                const main = document.getElementById('screen-main');
                const register = document.getElementById('screen-register');

                register.classList.remove('active');

                setTimeout(() => {
                    main.style.display = 'block';
                    setTimeout(() => {
                        main.style.opacity = '1';
                        main.style.transform = 'scale(1)';
                    }, 50);
                }, 400);
            }

            // Регистрация
            function register(event) {
                event.preventDefault();

                const name = document.getElementById('name').value.trim();
                const telegram = document.getElementById('telegram').value.trim();
                const password = document.getElementById('password').value;
                const messageEl = document.getElementById('message');
                const btn = document.getElementById('registerBtn');

                // Простая валидация
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

                // Отправка на сервер
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
                        // Перенаправление через 2 секунды
                        setTimeout(() => {
                            window.location.href = data.redirect || '/dashboard';
                        }, 2000);
                    } else {
                        showMessage('❌ ' + data.message, 'error');
                        btn.disabled = false;
                        btn.textContent = 'Зарегистрироваться';
                        // Встряхиваем всю форму при ошибке
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

@app.route('/get_ip')
def get_ip():
    return jsonify({'ip': get_client_ip()})

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        telegram = data.get('telegram', '').strip()
        password = data.get('password', '')

        # Валидация
        if not name or len(name) < 2:
            return jsonify({'success': False, 'message': 'Имя слишком короткое'})

        if not telegram.startswith('@') or len(telegram) < 3:
            return jsonify({'success': False, 'message': 'Неверный формат Telegram ника'})

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Пароль должен быть минимум 6 символов'})

        # Загружаем пользователей
        users = load_users()
        client_ip = get_client_ip()

        # ★★★ ИЗМЕНЕНИЕ: Проверка IP - только 1 регистрация ★★★
        ip_registrations = [u for u in users.values() if u.get('ip') == client_ip]
        if len(ip_registrations) >= 1:
            return jsonify({'success': False, 'message': '⚠️ С этого IP уже зарегистрирован аккаунт! Разрешена только 1 регистрация.'})

        # Проверка уникальности Telegram
        for user_id, user_data in users.items():
            if user_data.get('telegram') == telegram:
                return jsonify({'success': False, 'message': 'Этот Telegram уже зарегистрирован'})

        # Создаем нового пользователя
        user_id = str(len(users) + 1)
        users[user_id] = {
            'name': name,
            'telegram': telegram,
            'password_hash': hash_password(password),
            'ip': client_ip,
            'registered_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat()
        }

        save_users(users)

        # Сохраняем в сессию для авторизации
        session['user_id'] = user_id
        session['user_name'] = name

        return jsonify({
            'success': True,
            'message': f'Добро пожаловать, {name}!',
            'redirect': '/dashboard'
        })

    except Exception as e:
        print(f"Ошибка: {e}")  # Логирование
        return jsonify({'success': False, 'message': 'Ошибка на сервере'})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return '''
        <script>
            window.location.href = '/';
        </script>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AniCosmo - Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                color: white;
            }}
            .dashboard {{
                text-align: center;
                padding: 50px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                max-width: 500px;
            }}
            h1 {{ font-size: 48px; margin-bottom: 20px; }}
            .welcome {{ font-size: 24px; opacity: 0.8; margin-bottom: 15px; }}
            .info {{ opacity: 0.5; font-size: 14px; margin-bottom: 30px; }}
            .btn-logout {{
                padding: 12px 40px;
                background: rgba(255,107,107,0.2);
                border: 1px solid rgba(255,107,107,0.3);
                border-radius: 50px;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 16px;
            }}
            .btn-logout:hover {{
                background: rgba(255,107,107,0.3);
                transform: scale(1.05);
            }}
            .emoji {{ font-size: 60px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="emoji">🚀</div>
            <h1>Добро пожаловать!</h1>
            <div class="welcome">Привет, {session.get('user_name', 'Пользователь')}!</div>
            <div class="info">
                <p>Вы успешно зарегистрировались в AniCosmo</p>
                <p style="margin-top: 10px;">Скоро здесь появится контент</p>
            </div>
            <button class="btn-logout" onclick="logout()">Выйти</button>
        </div>
        <script>
            function logout() {{
                fetch('/logout')
                    .then(() => window.location.href = '/');
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return '', 200

@app.route('/background')
def background():
    try:
        return send_file('background.jpg')
    except:
        # Создаем простой градиент если файла нет
        from flask import Response
        import io
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (1920, 1080), color=(26, 26, 46))
        draw = ImageDraw.Draw(img)
        for i in range(0, 1080, 20):
            draw.rectangle([0, i, 1920, i+10], fill=(22, 33, 62))
        
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return Response(img_io.getvalue(), mimetype='image/jpeg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
