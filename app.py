from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Добро пожаловать на AniCosmo! 🎌</h1>
    <p>Ваш сайт работает на Render!</p>
    <p>Время: ''' + str(__import__('datetime').datetime.now()) + '''</p>
    <hr>
    <p>🔥 Скоро здесь будет что-то интересное про аниме!</p>
    '''

@app.route('/hello')
def hello():
    return 'Привет, мир!'

@app.route('/about')
def about():
    return 'О нас: AniCosmo — проект для любителей аниме.'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
