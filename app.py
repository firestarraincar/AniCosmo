from flask import Flask, send_file, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Файл для хранения данных
DATA_FILE = 'wins.json'

# Загружаем данные из файла
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'wins': [], 'next_id': 1}

# Сохраняем данные в файл
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
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
                padding: 40px 20px;
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

            .section-title {
                font-size: 32px;
                font-weight: 300;
                text-align: center;
                margin-bottom: 30px;
                letter-spacing: 2px;
                text-shadow: 0 0 30px rgba(0,0,0,0.5);
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

            .form-group {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-bottom: 12px;
            }
            .form-group input {
                flex: 1;
                min-width: 150px;
                padding: 12px 16px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
                background: rgba(255,255,255,0.06);
                color: white;
                font-size: 15px;
                transition: border 0.3s;
            }
            .form-group input:focus {
                outline: none;
                border-color: #ff6b6b;
            }
            .form-group input::placeholder {
                color: rgba(255,255,255,0.4);
            }
            .form-group .btn-submit {
                padding: 12px 30px;
                background: #ff6b6b;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.3s;
            }
            .form-group .btn-submit:hover {
                background: #ee5a24;
            }

            .code-hint {
                color: rgba(255,255,255,0.4);
                font-size: 13px;
                margin-top: 5px;
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
            .leaderboard-table .rank {
                color: #ffd93d;
                font-weight: 600;
            }
            .leaderboard-table .total {
                color: #6bcb77;
                font-weight: 600;
            }

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
            .win-item .win-id {
                font-size: 11px;
                color: rgba(255,255,255,0.2);
                margin-right: 8px;
            }
            .win-item .win-user { font-weight: 500; }
            .win-item .win-prize { color: #ffd93d; }
            .win-item .win-value { color: #6bcb77; font-weight: 600; }
            .win-item .win-tags {
                font-size: 13px;
                color: rgba(255,255,255,0.4);
            }
            .win-item .win-date {
                font-size: 12px;
                color: rgba(255,255,255,0.3);
            }
            .win-item .btn-delete {
                padding: 4px 14px;
                font-size: 12px;
                color: rgba(255,107,107,0.6);
                background: rgba(255,107,107,0.1);
                border: 1px solid rgba(255,107,107,0.2);
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .win-item .btn-delete:hover {
                background: rgba(255,107,107,0.2);
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
            .btn-back:hover {
                background: rgba(255,255,255,0.1);
                color: white;
            }

            .footer {
                text-align: center;
                color: rgba(255,255,255,0.12);
                font-size: 13px;
                letter-spacing: 3px;
                padding: 30px 0 10px;
            }

            .toast {
                padding: 10px 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                display: none;
            }
            .toast.success {
                display: block;
                background: rgba(107, 203, 119, 0.2);
                border: 1px solid rgba(107, 203, 119, 0.3);
                color: #6bcb77;
            }
            .toast.error {
                display: block;
                background: rgba(255, 107, 107, 0.2);
                border: 1px solid rgba(255, 107, 107, 0.3);
                color: #ff6b6b;
            }
            .toast.info {
                display: block;
                background: rgba(255, 217, 61, 0.15);
                border: 1px solid rgba(255, 217, 61, 0.2);
                color: #ffd93d;
            }

            .modal {
                display: none;
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.7);
                z-index: 100;
                justify-content: center;
                align-items: center;
            }
            .modal.active {
                display: flex;
            }
            .modal-content {
                background: rgba(30,30,50,0.95);
                backdrop-filter: blur(10px);
                padding: 30px;
                border-radius: 16px;
                max-width: 400px;
                width: 90%;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .modal-content h3 {
                margin-bottom: 15px;
                color: #ff6b6b;
            }
            .modal-content input {
                width: 100%;
                padding: 12px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
                background: rgba(255,255,255,0.06);
                color: white;
                font-size: 16px;
                margin-bottom: 15px;
                text-align: center;
            }
            .modal-content input:focus {
                outline: none;
                border-color: #ff6b6b;
            }
            .modal-buttons {
                display: flex;
                gap: 12px;
                justify-content: center;
            }
            .modal-buttons button {
                padding: 10px 30px;
                border-radius: 10px;
                border: none;
                font-size: 15px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .modal-buttons .btn-confirm {
                background: #ff6b6b;
                color: white;
            }
            .modal-buttons .btn-confirm:hover {
                background: #ee5a24;
            }
            .modal-buttons .btn-cancel {
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.6);
            }
            .modal-buttons .btn-cancel:hover {
                background: rgba(255,255,255,0.15);
            }

            @media (max-width: 600px) {
                #screen-main h1 { font-size: 32px; }
                .section-title { font-size: 24px; }
                .form-group input { min-width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">

            <!-- ЭКРАН 1 -->
            <div id="screen-main">
                <h1>AniCosmo — канал по Аникарду</h1>
                <div class="channel-block">
                    <div class="label">Канал</div>
                    <a href="https://t.me/AniCosmoDay" target="_blank">@AniCosmoDay</a>
                </div>
                <button class="btn" onclick="goForward()">Начать</button>
            </div>

            <!-- ЭКРАН 2 -->
            <div id="screen-content">
                <div style="text-align:center; margin-bottom:30px;">
                    <h2 style="font-size:38px; font-weight:300; letter-spacing:2px;">✨ Добро пожаловать!</h2>
                    <p style="opacity:0.6; margin-top:8px;">Управление розыгрышами AniCosmo</p>
                </div>

                <div id="toast" class="toast"></div>

                <!-- Форма добавления -->
                <div class="card">
                    <h3>➕ Добавить выигрыш</h3>
                    <div class="form-group">
                        <input type="text" id="winCode" placeholder="Код (132547)">
                        <input type="text" id="winUser" placeholder="Имя участника">
                        <input type="text" id="winPrize" placeholder="Что выиграл">
                        <input type="number" id="winValue" placeholder="Ценность в ПТ">
                    </div>
                    <div class="form-group">
                        <input type="text" id="winTags" placeholder="Теги (через запятую)">
                        <button class="btn-submit" onclick="addWin()">Опубликовать</button>
                    </div>
                    <div class="code-hint">🔑 Код для публикации: 132547 (введите в поле выше)</div>
                </div>

                <!-- Недавние выигрыши -->
                <div class="card">
                    <h3>📋 Недавние выигрыши</h3>
                    <div id="recentWins">
                        <div style="opacity:0.4; text-align:center; padding:20px;">Загрузка...</div>
                    </div>
                </div>

                <!-- Лидерборд -->
                <div class="card">
                    <h3>🏆 Лидерборд (по ценности призов в ПТ)</h3>
                    <div id="leaderboard">
                        <div style="opacity:0.4; text-align:center; padding:20px;">Загрузка...</div>
                    </div>
                </div>

                <div style="text-align:center;">
                    <button class="btn-back" onclick="goBack()">← Назад</button>
                </div>
            </div>

            <div class="footer">ANICOSMO</div>
        </div>

        <!-- Модальное окно для удаления -->
        <div class="modal" id="deleteModal">
            <div class="modal-content">
                <h3>🗑️ Удалить выигрыш?</h3>
                <p style="opacity:0.6; margin-bottom:15px;">Введите код для подтверждения</p>
                <input type="text" id="deleteCodeInput" placeholder="Код (132547)">
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="closeDeleteModal()">Отмена</button>
                    <button class="btn-confirm" onclick="confirmDelete()">Удалить</button>
                </div>
            </div>
        </div>

        <script>
            let deleteTargetId = null;

            // Переходы между экранами
            function goForward() {
                const main = document.getElementById('screen-main');
                main.style.opacity = '0';
                main.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    main.style.display = 'none';
                    const content = document.getElementById('screen-content');
                    content.style.display = 'block';
                    setTimeout(() => content.classList.add('active'), 50);
                    loadData();
                }, 500);
            }

            function goBack() {
                const content = document.getElementById('screen-content');
                content.classList.remove('active');
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

            function showToast(message, type = 'info') {
                const toast = document.getElementById('toast');
                toast.textContent = message;
                toast.className = 'toast ' + type;
                setTimeout(() => { toast.className = 'toast'; }, 5000);
            }

            async function loadData() {
                try {
                    const res = await fetch('/api/wins');
                    const data = await res.json();
                    renderWins(data.wins);
                    renderLeaderboard(data.wins);
                } catch (e) {
                    console.error('Ошибка загрузки:', e);
                }
            }

            function renderWins(wins) {
                const container = document.getElementById('recentWins');
                if (!wins || wins.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4; text-align:center; padding:20px;">Пока нет выигрышей</div>';
                    return;
                }
                const sorted = [...wins].reverse().slice(0, 20);
                container.innerHTML = sorted.map(w => `
                    <div class="win-item">
                        <div>
                            <span class="win-id">#${w.id}</span>
                            <span class="win-user">${w.user}</span>
                            <span class="win-tags">${w.tags ? ' ' + w.tags.map(t => '#' + t).join(' ') : ''}</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                            <span class="win-prize">${w.prize}</span>
                            <span class="win-value">${w.value} ПТ</span>
                            <span class="win-date">${w.date}</span>
                            <button class="btn-delete" onclick="openDeleteModal(${w.id})">✕</button>
                        </div>
                    </div>
                `).join('');
            }

            function renderLeaderboard(wins) {
                const container = document.getElementById('leaderboard');
                if (!wins || wins.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4; text-align:center; padding:20px;">Нет данных для лидерборда</div>';
                    return;
                }
                const stats = {};
                wins.forEach(w => {
                    if (!stats[w.user]) stats[w.user] = { total: 0, count: 0 };
                    stats[w.user].total += w.value;
                    stats[w.user].count += 1;
                });
                const sorted = Object.entries(stats)
                    .sort((a, b) => b[1].total - a[1].total)
                    .slice(0, 10);

                if (sorted.length === 0) {
                    container.innerHTML = '<div style="opacity:0.4; text-align:center; padding:20px;">Нет данных</div>';
                    return;
                }

                let html = `<table class="leaderboard-table">
                    <tr><th>#</th><th>Участник</th><th>Кол-во</th><th>Сумма ПТ</th></tr>`;
                sorted.forEach(([user, data], i) => {
                    const rank = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i+1}`;
                    html += `<tr>
                        <td class="rank">${rank}</td>
                        <td><strong>${user}</strong></td>
                        <td>${data.count} раз</td>
                        <td class="total">${data.total} ПТ</td>
                    </tr>`;
                });
                html += '</table>';
                container.innerHTML = html;
            }

            // Добавить выигрыш
            async function addWin() {
                const code = document.getElementById('winCode').value.trim();
                const user = document.getElementById('winUser').value.trim();
                const prize = document.getElementById('winPrize').value.trim();
                const value = parseInt(document.getElementById('winValue').value);
                const tagsRaw = document.getElementById('winTags').value.trim();

                // ПРОВЕРКА КОДА
                if (code !== '132547') {
                    showToast('❌ Неверный код! Нужно ввести 132547', 'error');
                    return;
                }
                if (!user || !prize || !value) {
                    showToast('❌ Заполните все поля (имя, приз, ценность в ПТ)!', 'error');
                    return;
                }
                if (value <= 0) {
                    showToast('❌ Ценность должна быть больше 0!', 'error');
                    return;
                }

                const tags = tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(t => t) : [];

                try {
                    const res = await fetch('/api/add', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user, prize, value, tags })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('✅ Выигрыш добавлен!', 'success');
                        document.getElementById('winCode').value = '';
                        document.getElementById('winUser').value = '';
                        document.getElementById('winPrize').value = '';
                        document.getElementById('winValue').value = '';
                        document.getElementById('winTags').value = '';
                        loadData();
                    } else {
                        showToast('❌ ' + result.error, 'error');
                    }
                } catch (e) {
                    showToast('❌ Ошибка сервера', 'error');
                }
            }

            // Открыть модалку удаления
            function openDeleteModal(id) {
                deleteTargetId = id;
                document.getElementById('deleteModal').classList.add('active');
                document.getElementById('deleteCodeInput').value = '';
                document.getElementById('deleteCodeInput').focus();
            }

            function closeDeleteModal() {
                document.getElementById('deleteModal').classList.remove('active');
                deleteTargetId = null;
            }

            // Подтвердить удаление
            async function confirmDelete() {
                const code = document.getElementById('deleteCodeInput').value.trim();
                // ПРОВЕРКА КОДА
                if (code !== '132547') {
                    showToast('❌ Неверный код! Нужно ввести 132547', 'error');
                    return;
                }
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
                        closeDeleteModal();
                        loadData();
                    } else {
                        showToast('❌ ' + result.error, 'error');
                    }
                } catch (e) {
                    showToast('❌ Ошибка сервера', 'error');
                }
            }

            // Закрыть модалку по Escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') closeDeleteModal();
            });
        </script>
    </body>
    </html>
    '''

# === API ===

@app.route('/api/wins')
def get_wins():
    data = load_data()
    return jsonify({'wins': data['wins']})

@app.route('/api/add', methods=['POST'])
def add_win():
    data = load_data()
    req = request.json

    user = req.get('user', '').strip()
    prize = req.get('prize', '').strip()
    value = req.get('value', 0)
    tags = req.get('tags', [])

    if not user or not prize or value <= 0:
        return jsonify({'success': False, 'error': 'Заполните все поля'})

    win = {
        'id': data['next_id'],
        'user': user,
        'prize': prize,
        'value': value,
        'tags': tags,
        'date': datetime.now().strftime('%d.%m.%Y %H:%M')
    }
    data['wins'].append(win)
    data['next_id'] += 1
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/delete', methods=['POST'])
def delete_win():
    data = load_data()
    win_id = request.json.get('id')

    new_wins = [w for w in data['wins'] if w['id'] != win_id]
    if len(new_wins) == len(data['wins']):
        return jsonify({'success': False, 'error': 'Запись не найдена'})

    data['wins'] = new_wins
    save_data(data)
    return jsonify({'success': True})

@app.route('/background')
def background():
    return send_file('background.jpg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
