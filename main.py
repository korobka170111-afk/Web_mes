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

db_sessions.global_init("db/blogs.db")
db_sess = db_sessions.create_session()
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('blogs.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            text TEXT,
            time TEXT
        )
    ''')
    conn.close()


@app.route('/messages')
def messages():
    conn = sqlite3.connect('blogs.db')
    messages = conn.execute('SELECT sender, text, time FROM messages').fetchall()
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

    time_now = datetime.now().strftime('%H:%M')

    conn = sqlite3.connect('blogs.db')
    conn.execute('INSERT INTO messages (sender, text, time) VALUES (?, ?, ?)',
                 (sender, text, time_now))
    conn.commit()
    conn.close()

    print(f"От: {sender} - {text}")
    return 'OK', 200

@app.route('/')
@app.route('/home')
def index():
    db_sessions.global_init("db/blogs.db")
    db_sess = db_sessions.create_session()
    user = db_sess.query(User).first()
    return render_template('index.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


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

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html')

init_db()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)