from flask import Flask, send_file
import os

app = Flask(__name__)

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

            /* === ЭКРАН 2: Контент === */
            #screen-content {
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

            #screen-content.active {
                opacity: 1;
                pointer-events: auto;
            }

            #screen-content .content-box {
                text-align: center;
                max-width: 800px;
            }

            #screen-content .content-box h2 {
                font-size: 48px;
                font-weight: 300;
                letter-spacing: 4px;
                margin-bottom: 30px;
                text-shadow: 0 0 40px rgba(0,0,0,0.5);
            }

            #screen-content .content-box p {
                font-size: 20px;
                opacity: 0.8;
                line-height: 1.8;
                text-shadow: 0 0 20px rgba(0,0,0,0.5);
            }

            /* Кнопка НАЗАД */
            .btn-back {
                margin-top: 40px;
                padding: 12px 40px;
                font-size: 16px;
                font-weight: 400;
                letter-spacing: 2px;
                color: rgba(255,255,255,0.6);
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
                backdrop-filter: blur(4px);
            }

            .btn-back:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.3);
                color: white;
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

        <!-- ЭКРАН 1: Главный -->
        <div id="screen-main">
            <h1>AniCosmo — канал по Аникарду</h1>
            <div class="channel-block">
                <div class="label">Канал</div>
                <a href="https://t.me/AniCosmoDay" target="_blank">@AniCosmoDay</a>
            </div>
            <button class="btn-start" onclick="goForward()">Начать</button>
        </div>

        <!-- ЭКРАН 2: Контент -->
        <div id="screen-content">
            <div class="content-box">
                <h2>✨ Добро пожаловать!</h2>
                <p>Здесь будет ваш контент.</p>
                <p style="margin-top:20px; font-size:16px; opacity:0.5;">
                    (Вы сможете заменить это на что угодно позже)
                </p>
                <button class="btn-back" onclick="goBack()">← Назад</button>
            </div>
        </div>

        <div class="footer">ANICOSMO</div>

        <script>
            function goForward() {
                const main = document.getElementById('screen-main');
                main.style.opacity = '0';
                main.style.transform = 'scale(0.95)';

                setTimeout(() => {
                    main.style.display = 'none';
                    document.getElementById('screen-content').classList.add('active');
                }, 800);
            }

            function goBack() {
                const main = document.getElementById('screen-main');
                const content = document.getElementById('screen-content');

                content.classList.remove('active');

                setTimeout(() => {
                    main.style.display = 'block';
                    setTimeout(() => {
                        main.style.opacity = '1';
                        main.style.transform = 'scale(1)';
                    }, 50);
                }, 400);
            }
        </script>

    </body>
    </html>
    '''

@app.route('/background')
def background():
    return send_file('background.jpg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
