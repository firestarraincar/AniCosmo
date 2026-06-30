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
                background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
                color: white;
                overflow: hidden;
                transition: background 0.5s;
            }

            /* === ЭКРАН 1: Главный === */
            #screen-main {
                text-align: center;
                z-index: 10;
                transition: opacity 0.8s, transform 0.8s;
            }

            #screen-main h1 {
                font-size: 72px;
                font-weight: 300;
                letter-spacing: 8px;
                text-shadow: 0 0 40px rgba(255, 107, 107, 0.3);
                margin-bottom: 50px;
            }

            #screen-main .btn-start {
                padding: 16px 60px;
                font-size: 20px;
                font-weight: 500;
                letter-spacing: 3px;
                color: white;
                background: transparent;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.4s;
                text-transform: uppercase;
            }

            #screen-main .btn-start:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.6);
                transform: scale(1.03);
                box-shadow: 0 0 30px rgba(255, 255, 255, 0.05);
            }

            /* === ЭКРАН 2: Контент (изначально скрыт) === */
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
            }

            #screen-content .content-box p {
                font-size: 20px;
                opacity: 0.7;
                line-height: 1.8;
            }

            /* Маленький индикатор внизу */
            .footer {
                position: fixed;
                bottom: 30px;
                left: 0;
                width: 100%;
                text-align: center;
                color: rgba(255,255,255,0.15);
                font-size: 13px;
                letter-spacing: 2px;
                z-index: 1;
            }
        </style>
    </head>
    <body>

        <!-- ЭКРАН 1: Главный -->
        <div id="screen-main">
            <h1>Канал</h1>
            <button class="btn-start" onclick="start()">Начать</button>
        </div>

        <!-- ЭКРАН 2: Контент (пока скрыт) -->
        <div id="screen-content">
            <div class="content-box">
                <h2>✨ Добро пожаловать!</h2>
                <p>Здесь будет ваш контент.</p>
                <p style="margin-top:20px; font-size:16px; opacity:0.5;">
                    (Вы сможете заменить это на что угодно позже)
                </p>
            </div>
        </div>

        <div class="footer">ANICOSMO</div>

        <script>
            function start() {
                // Плавно скрываем главный экран
                const main = document.getElementById('screen-main');
                main.style.opacity = '0';
                main.style.transform = 'scale(0.95)';

                // Через 0.8s показываем контент
                setTimeout(() => {
                    main.style.display = 'none';
                    document.getElementById('screen-content').classList.add('active');
                    // Меняем фон
                    document.body.style.background = 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)';
                }, 800);
            }
        </script>

    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
