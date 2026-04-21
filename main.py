from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlalchemy
from data.users import User
from data import db_sessions
from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime
from forms.user import RegisterForm
from data import db_sessions
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import random
import string


db_sessions.global_init("db/blogs.db")
db_sess = db_sessions.create_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'



@app.route('/')
@app.route('/home')
def index():
    db_sessions.global_init("db/blogs.db")
    db_sess = db_sessions.create_session()
    user = db_sess.query(User).first()
    return render_template('index.html', user=user)


def generate_code():
    return ''.join(random.choices(string.digits, k=8))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        sex = request.form.get('sex')

        if password != confirm_password:
            return render_template('register.html', message="Пароли не совпадают")

        if db_sess.query(User).filter(User.email == email).first():
            return render_template('register.html', message="Такой пользователь уже есть")

        user = User(
            name=name,
            surname=surname,
            email=email,
            sex=sex,
            hashed_password=generate_password_hash(password)
        )
        user.connect_code = generate_code()

        db_sess.add(user)
        db_sess.commit()

        session['user_id'] = user.id

        return redirect('/code')

    return render_template('register.html')

@app.route('/code')
def code():
    if 'user_id' not in session:
        return redirect('/login')

    user = db_sess.query(User).filter(User.id == session['user_id']).first()
    if user.tablet_ip:
        return redirect('/messages')

    return render_template('code.html', code=user.connect_code)


@app.route('/connect', methods=['GET'])
def connect_tablet():
    code = request.args.get('code')
    tablet_ip = request.remote_addr

    print(f"Получен код {code} от пользователя с айпи: {tablet_ip}")

    user = db_sess.query(User).filter(User.connect_code == code).first()

    if user:
        user.tablet_ip = tablet_ip
        db_sess.commit()
        return f"Устройство подключёно к пользователю {user.name}", 200
    else:
        return "Неверный код", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db_sess.query(User).filter(User.email == email).first()
        if user and check_password_hash(user.hashed_password, password):
            session['user_id'] = user.id
            return redirect('/code')
        else:
            return render_template('login.html', message="Неверный email или пароль")

    return render_template('login.html')


@app.route('/messages')
def messages():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = sqlite3.connect('db/blogs.db')
    messages = conn.execute(
        'SELECT sender, text, time FROM messages WHERE user_id = ? ORDER BY id DESC',(user_id,)).fetchall()
    conn.close()
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Сообщения из Макс</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .message { background: white; margin: 10px 0; padding: 10px; border-radius: 8px; }
        .sender { font-weight: bold; color: #007bff; }
        .time { font-size: 12px; color: gray; }
        .text { margin-top: 5px; }
    </style>
</head>
<body>
    <h1> Сообщения из Макс</h1>
    <div id="messages">
        {% for msg in messages %}
        <div class="message">
            <div class="sender">{{ msg[0] }}</div>
            <div class="time">{{ msg[2] }}</div>
            <div class="text">{{ msg[1] }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
''', messages=messages)


@app.route('/add', methods=['POST'])
def add_message():
    sender = request.form.get('sender')
    text = request.form.get('text')
    tablet_ip = request.remote_addr

    user = db_sess.query(User).filter(User.tablet_ip == tablet_ip).first()
    if not user:
        print(f"Неизвестное устройство с IP: {tablet_ip}")
        return 'OK', 200

    time_now = datetime.now().strftime('%H:%M')

    conn = sqlite3.connect('db/blogs.db')
    conn.execute(
        'INSERT INTO messages (sender, text, time, user_id) VALUES (?, ?, ?, ?)',
        (sender, text, time_now, user.id)
    )
    conn.commit()
    conn.close()

    print(f"Пользователь {user.name}: {sender} -> {text}")
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)