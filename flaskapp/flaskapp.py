from collections import Counter
from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import csv

app = Flask(__name__)

DATABASE = '/var/www/html/flaskapp/natlpark.db'

app.config.from_object(__name__)

conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
(username TEXT, password TEXT, email TEXT, firstname TEXT, lastname TEXT)''')
conn.commit()
conn.close()

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')

        conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)",
        (username, password, firstname, lastname, email))
        conn.commit()

        return redirect(url_for('profile', username=username))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid username or password."

    return render_template('login.html')

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT * FROM natlpark""")
    return '<br>'.join(str(row) for row in rows)

@app.route("/state/<state>")
def sortby(state):
    rows = execute_query("""SELECT * FROM natlpark WHERE state = ?""",
                         [state.title()])
    return '<br>'.join(str(row) for row in rows)

@app.route('/countme/<input_str>')
def count_me(input_str):
    input_counter = Counter(input_str)
    response = []
    for letter, count in input_counter.most_common():
        response.append('"{}": {}'.format(letter, count))
    return '<br>'.join(response)

if __name__ == '__main__':
        app.run(debug=True)