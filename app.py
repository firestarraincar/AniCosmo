from flask import Flask, send_file, request, jsonify, session, redirect
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'anicosmo-secret-key-2026'

DATA_FILE = 'users.json'
ANNOUNCEMENTS_FILE = 'announcements.json'
SETTINGS_FILE = 'settings.json'
SHOP_FILE = 'shop.json'
SKIN_REQUESTS_FILE = 'skin_requests.json'

def load_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        if file == DATA_FILE:
            return {}
        elif file == ANNOUNCEMENTS_FILE:
            return []
        elif file == SETTINGS_FILE:
            return {'code': '132547', 'private_mode': False}
        elif file == SHOP_FILE:
            return {
                'items': [
                    {'id': 1, 'name': '🛡️ Защитник', 'price': 100, 'type': 'rank'},
                    {'id': 2, 'name': '⚔️ Воин', 'price': 200, 'type': 'rank'},
                    {'id': 3, 'name': '👑 Король', 'price': 500, 'type': 'rank'},
                    {'id': 4, 'name': '🌟 Легенда', 'price': 1000, 'type': 'rank'},
                    {'id': 5, 'name': '👕 Красная футболка', 'price': 50, 'type': 'skin'},
                    {'id': 6, 'name': '👕 Синяя футболка', 'price': 50, 'type': 'skin'},
                ],
                'purchases': {}
            }
        elif file == SKIN_REQUESTS_FILE:
            return []
        return {}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    return load_json(DATA_FILE)

def save_users(users):
    save_json(DATA_FILE, users)

def load_announcements():
    return load_json(ANNOUNCEMENTS_FILE)

def save_announcements(data):
    save_json(ANNOUNCEMENTS_FILE, data)

def load_settings():
    return load_json(SETTINGS_FILE)

def save_settings(data):
    save_json(SETTINGS_FILE, data)

def load_shop():
    return load_json(SHOP_FILE)

def save_shop(data):
    save_json(SHOP_FILE, data)

def load_skin_requests():
    return load_json(SKIN_REQUESTS_FILE)

def save_skin_requests(data):
    save_json(SKIN_REQUESTS_FILE, data)

def register_user(username, password, telegram=''):
    users = load_users()
    if username in users:
        return {'success': False, 'error': 'Пользователь уже существует'}
    if len(password) < 4:
        return {'success': False, 'error': 'Пароль минимум 4 символа'}
    if len(username) < 3:
        return {'success': False, 'error': 'Логин минимум 3 символа'}
    
    users[username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'telegram': telegram,
        'role': 'user',
        'pt': 100,
        'rank': 'Новичок',
        'skin': 'Стандартная',
        'registered': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'banned': False,
        'purchases': []
    }
    save_users(users)
    return {'success': True}

def login_user(username, password):
    users = load_users()
    if username not in users:
        return {'success': False, 'error': 'Пользователь не найден'}
    if users[username].get('banned', False):
        return {'success': False, 'error': 'Аккаунт заблокирован'}
    if users[username]['password'] != hashlib.sha256(password.encode()).hexdigest():
        return {'success': False, 'error': 'Неверный пароль'}
    
    session['authorized'] = True
    session['username'] = username
    session['role'] = users[username].get('role', 'user')
    return {'success': True}

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
                max-width: 420px;
                border: 1px solid rgba(255,255,255,0.08);
                text-align: center;
            }
            .login-box h1 { font-size: 32px; color: #ff6b6b; margin-bottom: 5px; }
            .login-box .subtitle { font-size: 14px; opacity: 0.4; margin-bottom: 25px; }
            .login-box .tabs { display: flex; gap: 10px; margin-bottom: 25px; }
            .login-box .tabs button {
                flex: 1; padding: 10px; border: none; border-radius: 10px;
                background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.5);
                font-size: 16px; cursor: pointer; transition: all 0.3s;
            }
            .login-box .tabs button.active { background: rgba(255,107,107,0.2); color: #ff6b6b; }
            .login-box .tabs button:hover { background: rgba(255,255,255,0.1); }
            .login-box input {
                width: 100%; padding: 14px; border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
                background: rgba(255,255,255,0.06); color: white;
                font-size: 16px; margin-bottom: 12px; transition: border 0.3s;
            }
            .login-box input:focus { outline: none; border-color: #ff6b6b; }
            .login-box input::placeholder { color: rgba(255,255,255,0.3); }
            .login-box .btn-action {
                width: 100%; padding: 14px; border: none; border-radius: 10px;
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white; font-size: 18px; font-weight: 600; cursor: pointer;
                transition: all 0.3s; margin-top: 5px;
            }
            .login-box .btn-action:hover { transform: scale(1.02); box-shadow: 0 4px 20px rgba(238,90,36,0.3); }
            .login-box .btn-action.secondary { background: rgba(255,255,255,0.08); }
            .login-box .btn-action.secondary:hover { background: rgba(255,255,255,0.15); }
            .login-box .error { color: #ff6b6b; font-size: 14px; margin-top: 10px; min-height: 24px; }
            .login-box .success { color: #6bcb77; font-size: 14px; margin-top: 10px; min-height: 24px; }
            .login-box .form-group { display: none; }
            .login-box .form-group.active { display: block; }
            .login-box .info-text { font-size: 12px; opacity: 0.3; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="login-box">
            <h1>🔐 AniCosmo</h1>
            <div class="subtitle">Вход в панель управления</div>
            <div class="tabs">
                <button class="active" onclick="switchTab('login')">Вход</button>
                <button onclick="switchTab('register')">Регистрация</button>
            </div>
            <div id="loginForm" class="form-group active">
                <form method="POST" action="/login">
                    <input type="text" name="username" placeholder="Логин" required>
                    <input type="password" name="password" placeholder="Пароль" required>
                    <button type="submit" class="btn-action">Войти</button>
                    <div class="error" id="loginError"></div>
                </form>
            </div>
            <div id="registerForm" class="form-group">
                <form method="POST" action="/register">
                    <input type="text" name="username" placeholder="Придумайте логин" required>
                    <input type="password" name="password" placeholder="Пароль (мин. 4 символа)" required>
                    <input type="text" name="telegram" placeholder="@telegram (опционально)">
                    <button type="submit" class="btn-action secondary">Зарегистрироваться</button>
                    <div class="success" id="registerSuccess"></div>
                    <div class="error" id="registerError"></div>
                </form>
            </div>
            <div class="info-text">🔒 Все данные защищены</div>
        </div>
        <script>
            function switchTab(tab) {
                document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.form-group').forEach(f => f.classList.remove('active'));
                if (tab === 'login') {
                    document.querySelector('.tabs button:first-child').classList.add('active');
                    document.getElementById('loginForm').classList.add('active');
                } else {
                    document.querySelector('.tabs button:last-child').classList.add('active');
                    document.getElementById('registerForm').classList.add('active');
                }
            }
            const params = new URLSearchParams(window.location.search);
            const loginError = document.getElementById('loginError');
            const registerError = document.getElementById('registerError');
            const registerSuccess = document.getElementById('registerSuccess');
            if (params.get('login_error')) {
                loginError.textContent = '❌ ' + params.get('login_error');
            }
            if (params.get('register_error')) {
                registerError.textContent = '❌ ' + params.get('register_error');
                switchTab('register');
            }
            if (params.get('register_success')) {
                registerSuccess.textContent = '✅ ' + params.get('register_success');
                switchTab('login');
            }
        </script>
    </body>
    </html>
    '''

def main_page():
    username = session.get('username', 'Гость')
    role = session.get('role', 'user')
    
    html = '''
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
            .user-bar {
                position: fixed;
                top: 15px;
                right: 15px;
                z-index: 50;
                display: flex;
                gap: 12px;
                align-items: center;
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(8px);
                padding: 8px 16px;
                border-radius: 30px;
                border: 1px solid rgba(255,255,255,0.05);
            }
            .user-bar .username { font-size: 14px; opacity: 0.8; }
            .user-bar .role-badge {
                font-size: 11px;
                padding: 2px 12px;
                border-radius: 20px;
                background: rgba(255,215,0,0.15);
                color: #ffd93d;
            }
            .user-bar .role-badge.admin { background: rgba(255,107,107,0.2); color: #ff6b6b; }
            .user-bar .logout-link {
                color: rgba(255,255,255,0.3);
                text-decoration: none;
                font-size: 13px;
                transition: color 0.3s;
            }
            .user-bar .logout-link:hover { color: #ff6b6b; }
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
                padding: 30px; border-radius: 16px; max-width: 550px; width: 90%;
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
            .announcement-item {
                padding: 15px 0;
                border-bottom: 1px solid rgba(255,255,255,0.06);
            }
            .announcement-item:last-child { border-bottom: none; }
            .announcement-item .title { font-size: 20px; font-weight: 600; }
            .announcement-item .date { font-size: 12px; opacity: 0.3; }
            .announcement-item .text { margin: 8px 0; opacity: 0.8; }
            .announcement-item .reactions { display: flex; gap: 12px; margin-top: 8px; flex-wrap: wrap; }
            .announcement-item .reactions button {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 4px 12px;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }
            .announcement-item .reactions button:hover { background: rgba(255,255,255,0.15); }
            .announcement-item .comments {
                margin-top: 10px;
                padding-left: 20px;
                border-left: 2px solid rgba(255,255,255,0.05);
            }
            .announcement-item .comments .comment {
                padding: 6px 0;
                font-size: 14px;
                opacity: 0.7;
            }
            .announcement-item .comments .comment strong { color: #ff6b6b; opacity: 1; }
            .announcement-item .comments .comment-form {
                display: flex;
                gap: 10px;
                margin-top: 8px;
            }
            .announcement-item .comments .comment-form input {
                flex: 1;
                padding: 8px 12px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.05);
                color: white;
            }
            .announcement-item .comments .comment-form input:focus {
                outline: none;
                border-color: #ff6b6b;
            }
            .announcement-item .comments .comment-form button {
                padding: 8px 16px;
                border-radius: 10px;
                border: none;
                background: #ff6b6b;
                color: white;
                cursor: pointer;
            }
            .announcement-item .comments .comment-form button:hover { background: #ee5a24; }
            .shop-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .shop-item:last-child { border-bottom: none; }
            .shop-item .shop-name { font-size: 16px; }
            .shop-item .shop-price { color: #ffd93d; }
            .shop-item .shop-buy {
                padding: 6px 20px;
                border-radius: 20px;
                border: none;
                background: #6bcb77;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }
            .shop-item .shop-buy:hover { background: #4a9b56; transform: scale(1.02); }
            .shop-item .shop-buy:disabled { opacity: 0.3; cursor: not-allowed; }
            .shop-item .shop-owned { color: #6bcb77; font-size: 14px; }
            .profile-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                text-align: center;
                padding: 10px 0;
            }
            .profile-stats .stat {
                padding: 15px;
                background: rgba(255,255,255,0.03);
                border-radius: 12px;
            }
            .profile-stats .stat .number {
                font-size: 28px;
                font-weight: 700;
                color: #ffd93d;
            }
            .profile-stats .stat .label {
                font-size: 12px;
                opacity: 0.5;
                margin-top: 4px;
            }
            .request-item {
                padding: 10px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 8px;
            }
            .request-item .req-user { color: #ff6b6b; font-weight: 600; }
            .request-item .req-skin { color: #ffd93d; }
            .request-item .req-status {
                font-size: 12px;
                padding: 2px 12px;
                border-radius: 20px;
            }
            .request-item .req-status.pending { background: rgba(255,217,61,0.2); color: #ffd93d; }
            .request-item .req-status.approved { background: rgba(107,203,119,0.2); color: #6bcb77; }
            .request-item .req-status.rejected { background: rgba(255,107,107,0.2); color: #ff6b6b; }
            .req-actions button {
                padding: 4px 14px;
                border-radius: 10px;
                border: none;
                margin-left: 5px;
                cursor: pointer;
            }
            .req-actions .approve { background: #6bcb77; color: white; }
            .req-actions .reject { background: #ff6b6b; color: white; }
            @media (max-width: 600px) {
                #screen-main h1 { font-size: 32px; }
                .fab { width: 56px; height: 56px; font-size: 28px; bottom: 20px; right: 20px; }
                .user-bar { top: 10px; right: 10px; padding: 6px 12px; }
                .user-bar .username { font-size: 12px; }
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="user-bar">
            <span class="username">👤 USERNAME_PLACEHOLDER</span>
            <span class="role-badge ROLE_CLASS_PLACEHOLDER">ROLE_PLACEHOLDER</span>
            <a href="/logout" class="logout-link">🚪</a>
        </div>
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
                    <p style="opacity:0.6; margin-top:8px;">Анонсы и события AniCosmo</p>
                </div>
                <div class="card" id="profileCard">
                    <h3>👤 Мой профиль</h3>
                    <div id="profileContent">Загрузка...</div>
                </div>
                <div class="card">
                    <h3>📢 Анонсы событий</h3>
                    <div id="announcementsList">Загрузка...</div>
                </div>
                <div class="card">
                    <h3>🛒 Магазин</h3>
                    <div id="shopContent">Загрузка...</div>
                </div>
                <div class="card" id="requestsCard">
                    <h3>📩 Заявки на скины</h3>
                    <div id="requestsContent">Загрузка...</div>
                </div>
                <div style="text-align:center;">
                    <button class="btn-back" onclick="goBack()">← Назад</button>
                </div>
            </div>
            <div class="footer">ANICOSMO</div>
        </div>
        <button class="fab" id="fab" onclick="openMainMenu()">+</button>
        <div class="modal" id="mainMenu">
            <div class="modal-content">
                <h3>📋 Меню</h3>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <button onclick="closeModal('mainMenu');openAnnouncementModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">📢 Создать анонс</button>
                    <button onclick="closeModal('mainMenu');openGivePTModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">💰 Выдать ПТ</button>
                    <button onclick="closeModal('mainMenu');openGiveSkinModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">👕 Выдать скин</button>
                    <button onclick="closeModal('mainMenu');openGiveRankModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">🏅 Выдать звание</button>
                    <button onclick="closeModal('mainMenu');openRequestSkinModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">📩 Предложить скин</button>
                    <button onclick="closeModal('mainMenu');openSettingsModal();" style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:white;font-size:16px;cursor:pointer;">⚙️ Настройки</button>
                    <button onclick="closeModal('mainMenu');" style="padding:12px;border-radius:10px;background:rgba(255,107,107,0.2);border:1px solid rgba(255,107,107,0.3);color:#ff6b6b;font-size:16px;cursor:pointer;">❌ Закрыть</button>
                </div>
            </div>
        </div>
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
        <div class="modal" id="givePTModal">
            <div class="modal-content">
                <h3>💰 Выдать ПТ</h3>
                <div class="form-group">
                    <input type="password" id="ptCode" placeholder="Введите код" oninput="checkPTCode()">
                    <div class="code-status" id="ptCodeStatus"></div>
                </div>
                <div class="form-group">
                    <input type="text" id="ptUser" placeholder="Имя пользователя" disabled>
                    <input type="number" id="ptAmount" placeholder="Количество ПТ" disabled>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('givePTModal')">Отмена</button>
                    <button class="btn-submit-modal" id="ptSubmitBtn" onclick="submitPT()" disabled>Выдать</button>
                </div>
            </div>
        </div>
        <div class="modal" id="giveSkinModal">
            <div class="modal-content">
                <h3>👕 Выдать скин</h3>
                <div class="form-group">
                    <input type="password" id="skinCode" placeholder="Введите код" oninput="checkSkinCode()">
                    <div class="code-status" id="skinCodeStatus"></div>
                </div>
                <div class="form-group">
                    <input type="text" id="skinUser" placeholder="Имя пользователя" disabled>
                    <input type="text" id="skinName" placeholder="Название скина" disabled>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('giveSkinModal')">Отмена</button>
                    <button class="btn-submit-modal" id="skinSubmitBtn" onclick="submitSkin()" disabled>Выдать</button>
                </div>
            </div>
        </div>
        <div class="modal" id="giveRankModal">
            <div class="modal-content">
                <h3>🏅 Выдать звание</h3>
                <div class="form-group">
                    <input type="password" id="rankCode" placeholder="Введите код" oninput="checkRankCode()">
                    <div class="code-status" id="rankCodeStatus"></div>
                </div>
                <div class="form-group">
                    <input type="text" id="rankUser" placeholder="Имя пользователя" disabled>
                    <input type="text" id="rankName" placeholder="Название звания" disabled>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('giveRankModal')">Отмена</button>
                    <button class="btn-submit-modal" id="rankSubmitBtn" onclick="submitRank()" disabled>Выдать</button>
                </div>
            </div>
        </div>
        <div class="modal" id="requestSkinModal">
            <div class="modal-content">
                <h3>📩 Предложить скин</h3>
                <div class="form-group">
                    <input type="text" id="reqSkinName" placeholder="Название скина">
                    <input type="text" id="reqSkinDesc" placeholder="Описание скина">
                    <input type="text" id="reqSkinEmoji" placeholder="Эмодзи (например, 👕)">
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('requestSkinModal')">Отмена</button>
                    <button class="btn-submit-modal" onclick="submitRequest()">Отправить заявку</button>
                </div>
            </div>
        </div>
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
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeModal('settingsModal')">Закрыть</button>
                </div>
            </div>
        </div>
        <script>
            var annCodeVerified = false;
            var ptCodeVerified = false;
            var skinCodeVerified = false;
            var rankCodeVerified = false;
            var settingsCodeVerified = false;
        
            function goForward() {
                var main = document.getElementById('screen-main');
                if (!main) {
                    console.error('screen-main not found');
                    return;
                }
                main.style.opacity = '0';
                main.style.transform = 'scale(0.95)';
                setTimeout(function() {
                    main.style.display = 'none';
                    var content = document.getElementById('screen-content');
                    if (content) {
                        content.style.display = 'block';
                        setTimeout(function() {
                            content.classList.add('active');
                            var fab = document.getElementById('fab');
                            if (fab) fab.classList.add('show');
                            loadData();
                        }, 50);
                    }
                }, 500);
            }
        
            function goBack() {
                var content = document.getElementById('screen-content');
                if (!content) return;
                content.classList.remove('active');
                var fab = document.getElementById('fab');
                if (fab) fab.classList.remove('show');
                setTimeout(function() {
                    content.style.display = 'none';
                    var main = document.getElementById('screen-main');
                    if (main) {
                        main.style.display = 'block';
                        setTimeout(function() {
                            main.style.opacity = '1';
                            main.style.transform = 'scale(1)';
                        }, 50);
                    }
                }, 400);
            }
        
            function openModal(id) { 
                var el = document.getElementById(id);
                if (el) el.classList.add('active'); 
            }
            function closeModal(id) { 
                var el = document.getElementById(id);
                if (el) el.classList.remove('active'); 
            }
        
            function openMainMenu() { openModal('mainMenu'); }
            function openAnnouncementModal() { 
                openModal('announcementModal'); 
                var codeInput = document.getElementById('annCode');
                if (codeInput) codeInput.focus();
            }
            function openGivePTModal() { 
                openModal('givePTModal'); 
                var codeInput = document.getElementById('ptCode');
                if (codeInput) codeInput.focus();
            }
            function openGiveSkinModal() { 
                openModal('giveSkinModal'); 
                var codeInput = document.getElementById('skinCode');
                if (codeInput) codeInput.focus();
            }
            function openGiveRankModal() { 
                openModal('giveRankModal'); 
                var codeInput = document.getElementById('rankCode');
                if (codeInput) codeInput.focus();
            }
            function openRequestSkinModal() { openModal('requestSkinModal'); }
            function openSettingsModal() { 
                openModal('settingsModal'); 
                var codeInput = document.getElementById('settingsCode');
                if (codeInput) codeInput.focus();
                fetch('/api/settings')
                    .then(function(r) { return r.json(); })
                    .then(function(d) {
                        var pm = document.getElementById('privateMode');
                        if (pm) pm.checked = d.private_mode || false;
                    })
                    .catch(function(e) { console.error(e); });
            }
        
            function showToast(message, type) {
                type = type || 'info';
                var toast = document.createElement('div');
                toast.className = 'toast ' + type;
                toast.textContent = message;
                document.body.appendChild(toast);
                setTimeout(function() { 
                    if (toast && toast.parentNode) toast.remove(); 
                }, 4000);
            }
        
            function loadData() {
                loadProfile();
                loadAnnouncements();
                loadShop();
                loadRequests();
            }
        
            function loadProfile() {
                fetch('/api/profile')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        var container = document.getElementById('profileContent');
                        if (!container) return;
                        if (data.error) {
                            container.innerHTML = '<div style="opacity:0.4;text-align:center;">' + data.error + '</div>';
                            return;
                        }
                        container.innerHTML = '<div class="profile-stats">' +
                            '<div class="stat"><div class="number">' + (data.pt || 0) + '</div><div class="label">💰 ПТ</div></div>' +
                            '<div class="stat"><div class="number">' + (data.rank || 'Новичок') + '</div><div class="label">🏅 Звание</div></div>' +
                            '<div class="stat"><div class="number">' + (data.skin || 'Стандартная') + '</div><div class="label">👕 Скин</div></div>' +
                        '</div>' +
                        (data.purchases && data.purchases.length > 0 ? '<div style="margin-top:10px;font-size:13px;opacity:0.5;">🛒 Куплено: ' + data.purchases.join(', ') + '</div>' : '');
                    })
                    .catch(function(e) {
                        var container = document.getElementById('profileContent');
                        if (container) container.innerHTML = '<div style="opacity:0.4;text-align:center;">Ошибка загрузки</div>';
                    });
            }
        
            function loadAnnouncements() {
                fetch('/api/announcements')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        var container = document.getElementById('announcementsList');
                        if (!container) return;
                        if (!data || data.length === 0) {
                            container.innerHTML = '<div style="opacity:0.4;text-align:center;padding:20px;">Нет анонсов</div>';
                            return;
                        }
                        var html = '';
                        data.forEach(function(a) {
                            var reactions = '';
                            if (a.reactions) {
                                for (var key in a.reactions) {
                                    reactions += '<button onclick="react(' + a.id + ', \'' + key + '\')">' + key + ' ' + a.reactions[key] + '</button>';
                                }
                            }
                            var commentsHtml = '';
                            if (a.comments) {
                                a.comments.forEach(function(c) {
                                    commentsHtml += '<div class="comment"><strong>' + c.user + ':</strong> ' + c.text + ' <span style="opacity:0.3;font-size:11px;">' + c.date + '</span></div>';
                                });
                            }
                            html += '<div class="announcement-item">' +
                                '<div class="title">' + a.title + '</div>' +
                                '<div class="date">' + a.date + '</div>' +
                                '<div class="text">' + a.text + '</div>' +
                                '<div class="reactions">' + reactions + '</div>' +
                                '<div class="comments">' + commentsHtml +
                                    '<div class="comment-form">' +
                                        '<input type="text" id="commentInput_' + a.id + '" placeholder="Написать комментарий...">' +
                                        '<button onclick="addComment(' + a.id + ')">💬</button>' +
                                    '</div>' +
                                '</div>' +
                            '</div>';
                        });
                        container.innerHTML = html;
                    })
                    .catch(function(e) {
                        var container = document.getElementById('announcementsList');
                        if (container) container.innerHTML = '<div style="opacity:0.4;text-align:center;">Ошибка загрузки</div>';
                    });
            }
        
            function loadShop() {
                fetch('/api/shop')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        var container = document.getElementById('shopContent');
                        if (!container) return;
                        if (!data.items || data.items.length === 0) {
                            container.innerHTML = '<div style="opacity:0.4;text-align:center;padding:20px;">Магазин пуст</div>';
                            return;
                        }
                        var html = '';
                        data.items.forEach(function(item) {
                            var owned = data.owned && data.owned.indexOf(item.id) !== -1;
                            html += '<div class="shop-item">' +
                                '<div><span class="shop-name">' + (item.emoji || '') + ' ' + item.name + '</span> <span style="font-size:12px;opacity:0.3;">' + item.type + '</span></div>' +
                                '<div>' +
                                    '<span class="shop-price">' + item.price + ' ПТ</span> ' +
                                    (owned ? '<span class="shop-owned">✅ Куплено</span>' :
                                    '<button class="shop-buy" onclick="buyItem(' + item.id + ')">Купить</button>') +
                                '</div>' +
                            '</div>';
                        });
                        container.innerHTML = html;
                    })
                    .catch(function(e) {
                        var container = document.getElementById('shopContent');
                        if (container) container.innerHTML = '<div style="opacity:0.4;text-align:center;">Ошибка загрузки</div>';
                    });
            }
        
            function loadRequests() {
                fetch('/api/requests')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        var container = document.getElementById('requestsContent');
                        if (!container) return;
                        if (!data || data.length === 0) {
                            container.innerHTML = '<div style="opacity:0.4;text-align:center;padding:10px;">Нет заявок</div>';
                            return;
                        }
                        var html = '';
                        var isAdmin = document.querySelector('.role-badge.admin') !== null;
                        data.forEach(function(r) {
                            var statusClass = r.status || 'pending';
                            var statusText = statusClass === 'pending' ? '⏳ Ожидает' : statusClass === 'approved' ? '✅ Одобрено' : '❌ Отклонено';
                            html += '<div class="request-item">' +
                                '<div><span class="req-user">' + r.user + '</span> предлагает <span class="req-skin">' + r.name + '</span> ' + (r.emoji || '') +
                                (r.desc ? '<br><span style="font-size:12px;opacity:0.5;">' + r.desc + '</span>' : '') +
                                '</div>' +
                                '<div><span class="req-status ' + statusClass + '">' + statusText + '</span>' +
                                (isAdmin && statusClass === 'pending' ? ' <span class="req-actions"><button class="approve" onclick="approveRequest(' + r.id + ')">✅</button><button class="reject" onclick="rejectRequest(' + r.id + ')">❌</button></span>' : '') +
                                '</div>' +
                            '</div>';
                        });
                        container.innerHTML = html;
                    })
                    .catch(function(e) {
                        var container = document.getElementById('requestsContent');
                        if (container) container.innerHTML = '<div style="opacity:0.4;text-align:center;">Ошибка загрузки</div>';
                    });
            }
        
            // === АНОНСЫ ===
        
            function checkAnnCode() {
                var code = document.getElementById('annCode').value.trim();
                var status = document.getElementById('annCodeStatus');
                fetch('/api/settings')
                    .then(function(r) { return r.json(); })
                    .then(function(settings) {
                        var correct = settings.code || '132547';
                        if (code === correct) {
                            status.textContent = '✅ Код верный!';
                            status.className = 'code-status success';
                            document.getElementById('annTitle').disabled = false;
                            document.getElementById('annText').disabled = false;
                            document.getElementById('annSubmitBtn').disabled = false;
                            annCodeVerified = true;
                        } else if (code.length > 0) {
                            status.textContent = '❌ Неверный код';
                            status.className = 'code-status error';
                            document.getElementById('annTitle').disabled = true;
                            document.getElementById('annText').disabled = true;
                            document.getElementById('annSubmitBtn').disabled = true;
                            annCodeVerified = false;
                        } else {
                            status.textContent = '';
                            status.className = 'code-status';
                            document.getElementById('annTitle').disabled = true;
                            document.getElementById('annText').disabled = true;
                            document.getElementById('annSubmitBtn').disabled = true;
                            annCodeVerified = false;
                        }
                    })
                    .catch(function(e) { console.error(e); });
            }
        
            function submitAnnouncement() {
                if (!annCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                var title = document.getElementById('annTitle').value.trim();
                var text = document.getElementById('annText').value.trim();
                if (!title || !text) { showToast('❌ Заполните все поля!', 'error'); return; }
                fetch('/api/announcement', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title, text: text })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ Анонс опубликован!', 'success');
                        closeModal('announcementModal');
                        document.getElementById('annTitle').value = '';
                        document.getElementById('annText').value = '';
                        document.getElementById('annCode').value = '';
                        document.getElementById('annCodeStatus').textContent = '';
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка сервера', 'error'); });
            }
        
            function react(id, emoji) {
                fetch('/api/react', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: id, emoji: emoji })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) { loadData(); }
                })
                .catch(function(e) { console.error(e); });
            }
        
            function addComment(id) {
                var input = document.getElementById('commentInput_' + id);
                if (!input) return;
                var text = input.value.trim();
                if (!text) { showToast('❌ Напишите комментарий', 'error'); return; }
                fetch('/api/comment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: id, text: text })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        input.value = '';
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            // === МАГАЗИН ===
        
            function buyItem(itemId) {
                fetch('/api/buy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ ' + result.message, 'success');
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            // === ЗАЯВКИ ===
        
            function submitRequest() {
                var name = document.getElementById('reqSkinName').value.trim();
                var desc = document.getElementById('reqSkinDesc').value.trim();
                var emoji = document.getElementById('reqSkinEmoji').value.trim();
                if (!name) { showToast('❌ Введите название скина', 'error'); return; }
                fetch('/api/request_skin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, desc: desc, emoji: emoji })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ Заявка отправлена!', 'success');
                        closeModal('requestSkinModal');
                        document.getElementById('reqSkinName').value = '';
                        document.getElementById('reqSkinDesc').value = '';
                        document.getElementById('reqSkinEmoji').value = '';
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            function approveRequest(id) {
                fetch('/api/approve_request', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: id })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ Заявка одобрена!', 'success');
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            function rejectRequest(id) {
                fetch('/api/reject_request', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: id })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('❌ Заявка отклонена', 'info');
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            // === ВЫДАЧА ПТ ===
        
            function checkPTCode() {
                var code = document.getElementById('ptCode').value.trim();
                var status = document.getElementById('ptCodeStatus');
                fetch('/api/settings')
                    .then(function(r) { return r.json(); })
                    .then(function(settings) {
                        var correct = settings.code || '132547';
                        if (code === correct) {
                            status.textContent = '✅ Код верный!';
                            status.className = 'code-status success';
                            document.getElementById('ptUser').disabled = false;
                            document.getElementById('ptAmount').disabled = false;
                            document.getElementById('ptSubmitBtn').disabled = false;
                            ptCodeVerified = true;
                        } else if (code.length > 0) {
                            status.textContent = '❌ Неверный код';
                            status.className = 'code-status error';
                            document.getElementById('ptUser').disabled = true;
                            document.getElementById('ptAmount').disabled = true;
                            document.getElementById('ptSubmitBtn').disabled = true;
                            ptCodeVerified = false;
                        } else {
                            status.textContent = '';
                            status.className = 'code-status';
                            document.getElementById('ptUser').disabled = true;
                            document.getElementById('ptAmount').disabled = true;
                            document.getElementById('ptSubmitBtn').disabled = true;
                            ptCodeVerified = false;
                        }
                    })
                    .catch(function(e) { console.error(e); });
            }
        
            function submitPT() {
                if (!ptCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                var user = document.getElementById('ptUser').value.trim();
                var amount = parseInt(document.getElementById('ptAmount').value);
                if (!user) { showToast('❌ Введите имя пользователя', 'error'); return; }
                if (!amount || amount <= 0) { showToast('❌ Введите корректное количество', 'error'); return; }
                fetch('/api/give_pt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user: user, amount: amount })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ ' + result.message, 'success');
                        closeModal('givePTModal');
                        document.getElementById('ptUser').value = '';
                        document.getElementById('ptAmount').value = '';
                        document.getElementById('ptCode').value = '';
                        document.getElementById('ptCodeStatus').textContent = '';
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            // === ВЫДАЧА СКИНА ===
        
            function checkSkinCode() {
                var code = document.getElementById('skinCode').value.trim();
                var status = document.getElementById('skinCodeStatus');
                fetch('/api/settings')
                    .then(function(r) { return r.json(); })
                    .then(function(settings) {
                        var correct = settings.code || '132547';
                        if (code === correct) {
                            status.textContent = '✅ Код верный!';
                            status.className = 'code-status success';
                            document.getElementById('skinUser').disabled = false;
                            document.getElementById('skinName').disabled = false;
                            document.getElementById('skinSubmitBtn').disabled = false;
                            skinCodeVerified = true;
                        } else if (code.length > 0) {
                            status.textContent = '❌ Неверный код';
                            status.className = 'code-status error';
                            document.getElementById('skinUser').disabled = true;
                            document.getElementById('skinName').disabled = true;
                            document.getElementById('skinSubmitBtn').disabled = true;
                            skinCodeVerified = false;
                        } else {
                            status.textContent = '';
                            status.className = 'code-status';
                            document.getElementById('skinUser').disabled = true;
                            document.getElementById('skinName').disabled = true;
                            document.getElementById('skinSubmitBtn').disabled = true;
                            skinCodeVerified = false;
                        }
                    })
                    .catch(function(e) { console.error(e); });
            }
        
            function submitSkin() {
                if (!skinCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                var user = document.getElementById('skinUser').value.trim();
                var name = document.getElementById('skinName').value.trim();
                if (!user) { showToast('❌ Введите имя пользователя', 'error'); return; }
                if (!name) { showToast('❌ Введите название скина', 'error'); return; }
                fetch('/api/give_skin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user: user, name: name })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ ' + result.message, 'success');
                        closeModal('giveSkinModal');
                        document.getElementById('skinUser').value = '';
                        document.getElementById('skinName').value = '';
                        document.getElementById('skinCode').value = '';
                        document.getElementById('skinCodeStatus').textContent = '';
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            // === ВЫДАЧА ЗВАНИЯ ===
        
            function checkRankCode() {
                var code = document.getElementById('rankCode').value.trim();
                var status = document.getElementById('rankCodeStatus');
                fetch('/api/settings')
                    .then(function(r) { return r.json(); })
                    .then(function(settings) {
                        var correct = settings.code || '132547';
                        if (code === correct) {
                            status.textContent = '✅ Код верный!';
                            status.className = 'code-status success';
                            document.getElementById('rankUser').disabled = false;
                            document.getElementById('rankName').disabled = false;
                            document.getElementById('rankSubmitBtn').disabled = false;
                            rankCodeVerified = true;
                        } else if (code.length > 0) {
                            status.textContent = '❌ Неверный код';
                            status.className = 'code-status error';
                            document.getElementById('rankUser').disabled = true;
                            document.getElementById('rankName').disabled = true;
                            document.getElementById('rankSubmitBtn').disabled = true;
                            rankCodeVerified = false;
                        } else {
                            status.textContent = '';
                            status.className = 'code-status';
                            document.getElementById('rankUser').disabled = true;
                            document.getElementById('rankName').disabled = true;
                            document.getElementById('rankSubmitBtn').disabled = true;
                            rankCodeVerified = false;
                        }
                    })
                    .catch(function(e) { console.error(e); });
            }
        
            function submitRank() {
                if (!rankCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                var user = document.getElementById('rankUser').value.trim();
                var name = document.getElementById('rankName').value.trim();
                if (!user) { showToast('❌ Введите имя пользователя', 'error'); return; }
                if (!name) { showToast('❌ Введите название звания', 'error'); return; }
                fetch('/api/give_rank', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user: user, name: name })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ ' + result.message, 'success');
                        closeModal('giveRankModal');
                        document.getElementById('rankUser').value = '';
                        document.getElementById('rankName').value = '';
                        document.getElementById('rankCode').value = '';
                        document.getElementById('rankCodeStatus').textContent = '';
                        loadData();
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            // === НАСТРОЙКИ ===
        
            function checkSettingsCode() {
                var code = document.getElementById('settingsCode').value.trim();
                var status = document.getElementById('settingsCodeStatus');
                fetch('/api/settings')
                    .then(function(r) { return r.json(); })
                    .then(function(settings) {
                        var correct = settings.code || '132547';
                        if (code === correct) {
                            status.textContent = '✅ Код верный!';
                            status.className = 'code-status success';
                            document.getElementById('settingsNewCode').disabled = false;
                            document.getElementById('settingsChangeBtn').disabled = false;
                            settingsCodeVerified = true;
                        } else if (code.length > 0) {
                            status.textContent = '❌ Неверный код';
                            status.className = 'code-status error';
                            document.getElementById('settingsNewCode').disabled = true;
                            document.getElementById('settingsChangeBtn').disabled = true;
                            settingsCodeVerified = false;
                        } else {
                            status.textContent = '';
                            status.className = 'code-status';
                            document.getElementById('settingsNewCode').disabled = true;
                            document.getElementById('settingsChangeBtn').disabled = true;
                            settingsCodeVerified = false;
                        }
                    })
                    .catch(function(e) { console.error(e); });
            }
        
            function changeCode() {
                if (!settingsCodeVerified) { showToast('❌ Введите правильный код!', 'error'); return; }
                var newCode = document.getElementById('settingsNewCode').value.trim();
                if (!newCode || newCode.length < 4) { showToast('❌ Код должен быть минимум 4 символа', 'error'); return; }
                fetch('/api/settings/code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_code: newCode })
                })
                .then(function(r) { return r.json(); })
                .then(function(result) {
                    if (result.success) {
                        showToast('✅ Код изменён!', 'success');
                        closeModal('settingsModal');
                    } else { showToast('❌ ' + (result.error || 'Ошибка'), 'error'); }
                })
                .catch(function(e) { showToast('❌ Ошибка', 'error'); });
            }
        
            var privateModeCheck = document.getElementById('privateMode');
            if (privateModeCheck) {
                privateModeCheck.addEventListener('change', function() {
                    fetch('/api/settings/private', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ enabled: this.checked })
                    })
                    .catch(function(e) { console.error(e); });
                });
            }
        
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    document.querySelectorAll('.modal.active').forEach(function(m) { 
                        if (m) m.classList.remove('active'); 
                    });
                }
            });
        </script>
    </body>
    </html>
    '''
    
    html = html.replace('USERNAME_PLACEHOLDER', username)
    html = html.replace('ROLE_PLACEHOLDER', role)
    html = html.replace('ROLE_CLASS_PLACEHOLDER', 'admin' if role == 'admin' else '')
    
    return html

# === МАРШРУТЫ ===

@app.route('/')
def home():
    settings = load_settings()
    if settings.get('private_mode', False) and not session.get('authorized'):
        return login_page()
    return main_page()

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    result = login_user(username, password)
    if result['success']:
        return redirect('/')
    return redirect('/?login_error=' + result['error'])

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    telegram = request.form.get('telegram', '').strip()
    result = register_user(username, password, telegram)
    if result['success']:
        session['authorized'] = True
        session['username'] = username
        session['role'] = 'user'
        return redirect('/')
    return redirect('/?register_error=' + result['error'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/profile')
def api_profile():
    if 'username' not in session:
        return jsonify({'error': 'Не авторизован'})
    users = load_users()
    user = users.get(session['username'], {})
    return jsonify({
        'username': session['username'],
        'pt': user.get('pt', 0),
        'rank': user.get('rank', 'Новичок'),
        'skin': user.get('skin', 'Стандартная'),
        'purchases': user.get('purchases', [])
    })

@app.route('/api/announcements')
def api_announcements():
    return jsonify(load_announcements())

@app.route('/api/announcement', methods=['POST'])
def api_announcement():
    data = load_announcements()
    req = request.json
    announcement = {
        'id': len(data) + 1,
        'title': req.get('title', ''),
        'text': req.get('text', ''),
        'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'reactions': {},
        'comments': []
    }
    data.append(announcement)
    save_announcements(data)
    return jsonify({'success': True})

@app.route('/api/react', methods=['POST'])
def api_react():
    data = load_announcements()
    req = request.json
    for a in data:
        if a['id'] == req.get('id'):
            emoji = req.get('emoji')
            if emoji not in a['reactions']:
                a['reactions'][emoji] = 0
            a['reactions'][emoji] += 1
            save_announcements(data)
            return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/comment', methods=['POST'])
def api_comment():
    data = load_announcements()
    req = request.json
    for a in data:
        if a['id'] == req.get('id'):
            a['comments'].append({
                'user': session.get('username', 'Аноним'),
                'text': req.get('text', ''),
                'date': datetime.now().strftime('%d.%m.%Y %H:%M')
            })
            save_announcements(data)
            return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/shop')
def api_shop():
    shop = load_shop()
    if 'username' in session:
        users = load_users()
        user = users.get(session['username'], {})
        shop['owned'] = user.get('purchases', [])
    return jsonify(shop)

@app.route('/api/buy', methods=['POST'])
def api_buy():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Войдите в систему'})
    users = load_users()
    shop = load_shop()
    user = users.get(session['username'], {})
    item_id = request.json.get('item_id')
    item = next((i for i in shop['items'] if i['id'] == item_id), None)
    if not item:
        return jsonify({'success': False, 'error': 'Товар не найден'})
    if item_id in user.get('purchases', []):
        return jsonify({'success': False, 'error': 'Уже куплено'})
    if user.get('pt', 0) < item['price']:
        return jsonify({'success': False, 'error': 'Недостаточно ПТ'})
    users[session['username']]['pt'] = user.get('pt', 0) - item['price']
    if 'purchases' not in users[session['username']]:
        users[session['username']]['purchases'] = []
    users[session['username']]['purchases'].append(item_id)
    if item['type'] == 'rank':
        users[session['username']]['rank'] = item['name']
    elif item['type'] == 'skin':
        users[session['username']]['skin'] = item['name']
    save_users(users)
    return jsonify({'success': True, 'message': 'Покупка совершена!'})

@app.route('/api/give_pt', methods=['POST'])
def api_give_pt():
    req = request.json
    user = req.get('user', '')
    amount = req.get('amount', 0)
    users = load_users()
    if user not in users:
        return jsonify({'success': False, 'error': 'Пользователь не найден'})
    if amount <= 0:
        return jsonify({'success': False, 'error': 'Сумма должна быть больше 0'})
    users[user]['pt'] = users[user].get('pt', 0) + amount
    save_users(users)
    return jsonify({'success': True, 'message': f'Выдано {amount} ПТ пользователю {user}'})

@app.route('/api/give_skin', methods=['POST'])
def api_give_skin():
    req = request.json
    user = req.get('user', '')
    name = req.get('name', '')
    users = load_users()
    if user not in users:
        return jsonify({'success': False, 'error': 'Пользователь не найден'})
    if not name:
        return jsonify({'success': False, 'error': 'Введите название скина'})
    users[user]['skin'] = name
    save_users(users)
    return jsonify({'success': True, 'message': f'Скин "{name}" выдан пользователю {user}'})

@app.route('/api/give_rank', methods=['POST'])
def api_give_rank():
    req = request.json
    user = req.get('user', '')
    name = req.get('name', '')
    users = load_users()
    if user not in users:
        return jsonify({'success': False, 'error': 'Пользователь не найден'})
    if not name:
        return jsonify({'success': False, 'error': 'Введите название звания'})
    users[user]['rank'] = name
    save_users(users)
    return jsonify({'success': True, 'message': f'Звание "{name}" выдано пользователю {user}'})

@app.route('/api/requests')
def api_requests():
    return jsonify(load_skin_requests())

@app.route('/api/request_skin', methods=['POST'])
def api_request_skin():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Войдите в систему'})
    data = load_skin_requests()
    req = request.json
    request_item = {
        'id': len(data) + 1,
        'user': session['username'],
        'name': req.get('name', ''),
        'desc': req.get('desc', ''),
        'emoji': req.get('emoji', ''),
        'status': 'pending'
    }
    data.append(request_item)
    save_skin_requests(data)
    return jsonify({'success': True})

@app.route('/api/approve_request', methods=['POST'])
def api_approve_request():
    data = load_skin_requests()
    req_id = request.json.get('id')
    for r in data:
        if r['id'] == req_id:
            r['status'] = 'approved'
            save_skin_requests(data)
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Заявка не найдена'})

@app.route('/api/reject_request', methods=['POST'])
def api_reject_request():
    data = load_skin_requests()
    req_id = request.json.get('id')
    for r in data:
        if r['id'] == req_id:
            r['status'] = 'rejected'
            save_skin_requests(data)
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Заявка не найдена'})

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

@app.route('/background')
def background():
    return send_file('background.jpg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
