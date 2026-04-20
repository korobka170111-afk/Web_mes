from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlalchemy
from data.users import User
from data import db_sessions

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def index():
    db_sessions.global_init("db/blogs.db")
    db_sess = db_sessions.create_session()
    user = db_sess.query(User).all()
    return render_template('index.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')



if __name__ == '__main__':
    app.run(debug=True, port=8080)