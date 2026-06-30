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
        <title>AniCosmo — Аникард</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Arial, sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-image: url('/background');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                position: relative;
            }}

            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1;
            }}

            .content {{
                position: relative;
                z-index: 2;
                text-align: center;
                color: white;
                padding: 20px;
                max-width: 800px;
            }}

            h1 {{
                font-size: 48px;
                margin-bottom: 20px;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
                font-weight: bold;
            }}

            .subtitle {{
                font-size: 24px;
                margin-bottom: 40px;
                opacity: 0.9;
                text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
            }}

            .btn {{
                display: inline-block;
                padding: 18px 50px;
                font-size: 22px;
                font-weight: bold;
                color: white;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                border: none;
                border-radius: 50px;
                cursor: pointer;
                text-decoration: none;
                box-shadow: 0 4px 15px rgba(238, 90, 36, 0.4);
                transition: transform 0.3s, box-shadow 0.3s;
            }}

            .btn:hover {{
                transform: scale(1.05);
                box-shadow: 0 6px 25px rgba(238, 90, 36, 0.6);
            }}

            .footer {{
                position: fixed;
                bottom: 20px;
                left: 0;
                width: 100%;
                text-align: center;
                color: rgba(255,255,255,0.5);
                font-size: 14px;
                z-index: 2;
                text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
            }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="content">
            <h1>🎴 Сайт для канала AniCosmo<br>по Аникарду</h1>
            <p class="subtitle">Добро пожаловать в мир коллекционных карточек!</p>
            <a href="https://t.me/AniCosmoDay" class="btn" target="_blank">▶ Начать</a>
        </div>
        <div class="footer">© 2026 AniCosmo — Все права защищены</div>
    </body>
    </html>
    '''

@app.route('/background')
def background():
    return send_file('background.jpg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
