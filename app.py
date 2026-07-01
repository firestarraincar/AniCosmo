from flask import Flask, send_file, request, jsonify, session, render_template_string
import os
import json
import hashlib
import random
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'change-this-to-random-secret-key-12345'

# Файлы для хранения данных
USERS_FILE = 'users.json'
WINS_FILE = 'wins.json'
SHOP_FILE = 'shop.json'

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

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
    # Товары по умолчанию
    return {
        'items': [
            {'id': 1, 'name': '⭐ Премиум роль', 'price': 1000, 'icon': '👑'},
            {'id': 2, 'name': '🎨 Уникальный никнейм', 'price': 500, 'icon': '✨'},
            {'id': 3, 'name': '📢 Реклама в канале', 'price': 2000, 'icon': '📣'},
            {'id': 4, 'name': '🎮 Доступ к бете', 'price': 1500, 'icon': '🎯'},
            {'id': 5, 'name': '🖼 Кастомная рамка', 'price': 300, 'icon': '🖼'}
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

# === ГЛАВНАЯ СТРАНИЦА ===

@app.route('/')
def home():
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
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                width: 100%;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 48px;
                font-weight: 700;
                background: linear-gradient(135deg, #f093fb, #f5576c);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            .header .subtitle {
                opacity: 0.6;
                font-size: 18px;
                letter-spacing: 2px;
            }
            .main-menu {
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
                margin-bottom: 40px;
            }
            .main-menu button {
                padding: 15px 40px;
                font-size: 18px;
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
                box-shadow: 0 10px 30px rgba(245, 87, 108, 0.2);
            }
            .main-menu button.active {
                background: rgba(245, 87, 108, 0.2);
                border-color: #f5576c;
            }
            .content {
                background: rgba(255,255,255,0.05);
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
                margin-top: 40px;
                opacity: 0.3;
                font-size: 13px;
                letter-spacing: 3px;
            }
            .btn-logout {
                padding: 8px 20px;
                background: rgba(255,107,107,0.2);
                border: 1px solid rgba(255,107,107,0.2);
                border-radius: 50px;
                color: white;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
                margin-left: 20px;
            }
            .btn-logout:hover {
                background: rgba(255,107,107,0.3);
            }
            .user-info {
                display: inline-flex;
                align-items: center;
                gap: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌟 AniCosmo</h1>
                <div class="subtitle">Канал по Аникарду</div>
                <div style="margin-top: 15px;">
                    <a href="https://t.me/AniCosmoDay" target="_blank" style="color: #f5576c; text-decoration: none; font-size: 18px;">@AniCosmoDay</a>
                    <button class="btn-logout" onclick="logout()">Выйти</button>
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

        <script>
            let currentUser = null;

            // Загрузка данных пользователя
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

            // Показ раздела
            function showSection(section) {
                document.querySelectorAll('.content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.main-menu button').forEach(el => el.classList.remove('active'));
                
                document.getElementById(section + '-section').classList.add('active');
                document.getElementById('btn-' + section).classList.add('active');

                if (section === 'profile') renderProfile();
                if (section === 'shop') renderShop();
                if (section === 'wins') renderWins();
            }

            // === ПРОФИЛЬ ===
            function renderProfile() {
                if (!currentUser) return;
                const section = document.getElementById('profile-section');
                section.innerHTML = `
                    <div style="text-align: center;">
                        <div style="font-size: 60px; margin-bottom: 10px;">👤</div>
                        <h2 style="font-size: 32px; margin-bottom: 5px;">${currentUser.name}</h2>
                        <p style="opacity: 0.6; margin-bottom: 20px;">${currentUser.telegram}</p>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; max-width: 600px; margin: 0 auto;">
                            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;">
                                <div style="font-size: 28px; font-weight: bold; color: #f5576c;">${currentUser.points || 0}</div>
                                <div style="opacity: 0.5; font-size: 14px;">PT Баллов</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;">
                                <div style="font-size: 28px; font-weight: bold; color: #4ecdc4;">${currentUser.wins_count || 0}</div>
                                <div style="opacity: 0.5; font-size: 14px;">Побед</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;">
                                <div style="font-size: 28px; font-weight: bold; color: #ffe66d;">${currentUser.telegram}</div>
                                <div style="opacity: 0.5; font-size: 14px;">Telegram</div>
                            </div>
                        </div>
                        <div style="margin-top: 30px; opacity: 0.3; font-size: 12px;">
                            IP: ${currentUser.ip} • Зарегистрирован: ${new Date(currentUser.registered_at).toLocaleDateString()}
                        </div>
                    </div>
                `;
            }

            // === МАГАЗИН ===
            function renderShop() {
                const section = document.getElementById('shop-section');
                fetch('/api/shop')
                    .then(res => res.json())
                    .then(data => {
                        let itemsHtml = data.items.map(item => `
                            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; text-align: center;">
                                <div style="font-size: 40px;">${item.icon}</div>
                                <h3 style="margin: 10px 0;">${item.name}</h3>
                                <p style="color: #f5576c; font-weight: bold;">${item.price} PT</p>
                                <button onclick="buyItem(${item.id})" style="margin-top: 10px; padding: 10px 30px; background: rgba(245,87,108,0.3); border: 1px solid rgba(245,87,108,0.3); border-radius: 50px; color: white; cursor: pointer; transition: all 0.3s;">
                                    Купить
                                </button>
                            </div>
                        `).join('');

                        section.innerHTML = `
                            <h2 style="margin-bottom: 20px;">🛒 Магазин</h2>
                            <p style="opacity: 0.6; margin-bottom: 20px;">Ваши баллы: <strong style="color: #f5576c;">${currentUser ? currentUser.points || 0 : 0} PT</strong></p>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                                ${itemsHtml}
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

            // === РОЗЫГРЫШИ ===
            function renderWins() {
                const section = document.getElementById('wins-section');
                fetch('/api/wins')
                    .then(res => res.json())
                    .then(data => {
                        const recentWins = data.wins.slice(-10).reverse();
                        const topWins = [...data.wins].sort((a, b) => b.amount - a.amount).slice(0, 10);

                        section.innerHTML = `
                            <h2 style="margin-bottom: 20px;">🎰 Розыгрыши</h2>
                            
                            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; margin-bottom: 30px;">
                                <h3 style="margin-bottom: 15px;">➕ Добавить результат</h3>
                                <form onsubmit="addWin(event)" style="display: flex; flex-wrap: wrap; gap: 15px; align-items: end;">
                                    <div style="flex: 1; min-width: 150px;">
                                        <label style="display: block; font-size: 12px; opacity: 0.5; margin-bottom: 5px;">Telegram ник</label>
                                        <input type="text" id="win-telegram" placeholder="@username" style="width: 100%; padding: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; outline: none;">
                                    </div>
                                    <div style="flex: 1; min-width: 150px;">
                                        <label style="display: block; font-size: 12px; opacity: 0.5; margin-bottom: 5px;">Что выиграл</label>
                                        <input type="text" id="win-prize" placeholder="Например: 1000 PT" style="width: 100%; padding: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; outline: none;">
                                    </div>
                                    <div style="flex: 1; min-width: 150px;">
                                        <label style="display: block; font-size: 12px; opacity: 0.5; margin-bottom: 5px;">Сумма в PT</label>
                                        <input type="number" id="win-amount" placeholder="0" style="width: 100%; padding: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; outline: none;">
                                    </div>
                                    <button type="submit" style="padding: 12px 30px; background: rgba(245,87,108,0.3); border: 1px solid rgba(245,87,108,0.3); border-radius: 10px; color: white; cursor: pointer; transition: all 0.3s;">
                                        Добавить
                                    </button>
                                </form>
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                                <div>
                                    <h3 style="margin-bottom: 15px;">📋 Недавние выигрыши</h3>
                                    <div style="max-height: 300px; overflow-y: auto;">
                                        ${recentWins.length === 0 ? '<p style="opacity: 0.3;">Пока нет выигрышей</p>' : recentWins.map(win => `
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                                <span><strong style="color: #4ecdc4;">${win.telegram}</strong> - ${win.prize}</span>
                                                <span style="color: #f5576c;">+${win.amount} PT</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                <div>
                                    <h3 style="margin-bottom: 15px;">🏆 Топ по сумме PT</h3>
                                    <div style="max-height: 300px; overflow-y: auto;">
                                        ${topWins.length === 0 ? '<p style="opacity: 0.3;">Нет данных</p>' : topWins.map((win, index) => `
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                                <span>${index + 1}. <strong style="color: #ffe66d;">${win.telegram}</strong></span>
                                                <span style="color: #f5576c;">${win.amount} PT</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
            }

            function addWin(event) {
                event.preventDefault();
                const telegram = document.getElementById('win-telegram').value.trim();
                const prize = document.getElementById('win-prize').value.trim();
                const amount = parseInt(document.getElementById('win-amount').value);

                if (!telegram || !prize || !amount) {
                    alert('Заполните все поля!');
                    return;
                }

                fetch('/api/add_win', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ telegram, prize, amount })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ ' + data.message);
                        document.getElementById('win-telegram').value = '';
                        document.getElementById('win-prize').value = '';
                        document.getElementById('win-amount').value = '';
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

            // Инициализация
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
            'name': user['name'],
            'telegram': user['telegram'],
            'points': user.get('points', 0),
            'wins_count': len(user_wins),
            'ip': user['ip'],
            'registered_at': user['registered_at']
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
    
    if user.get('points', 0) < item['price']:
        return jsonify({'success': False, 'message': f'Недостаточно баллов! Нужно {item["price"]} PT'})
    
    user['points'] = user.get('points', 0) - item['price']
    user['purchases'] = user.get('purchases', []) + [{
        'item': item['name'],
        'price': item['price'],
        'date': datetime.now().isoformat()
    }]
    
    save_users(users)
    return jsonify({'success': True, 'message': f'Вы купили {item["name"]}!'})

@app.route('/api/wins')
def api_wins():
    wins = load_wins()
    return jsonify(wins)

@app.route('/api/add_win', methods=['POST'])
@login_required
def api_add_win():
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
    
    # Начисляем баллы победителю
    users = load_users()
    for user_id, user in users.items():
        if user['telegram'] == telegram:
            user['points'] = user.get('points', 0) + amount
            user['last_win'] = datetime.now().isoformat()
            save_users(users)
            break
    
    return jsonify({'success': True, 'message': 'Выигрыш добавлен!'})

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
        
        # Проверка IP - только 1 регистрация
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
            'points': 100,  # Начальный бонус
            'registered_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'purchases': []
        }
        
        save_users(users)
        session['user_id'] = user_id
        session['user_name'] = name
        
        return jsonify({
            'success': True,
            'message': f'Добро пожаловать, {name}! Вы получили 100 PT бонуса!',
            'redirect': '/'
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
        for i in range(0, 1080, 20):
            draw.rectangle([0, i, 1920, i+10], fill=(48, 43, 99))
        
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return Response(img_io.getvalue(), mimetype='image/jpeg')

@app.route('/get_ip')
def get_ip():
    return jsonify({'ip': get_client_ip()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
