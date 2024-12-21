

#utils/auth.py

import sqlite3

def login(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    return user

def signup(conn, username, password, email):
    try:
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité SQLite : {e}")
        return False

def create_user_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT
    )''')
    conn.commit()


def delete_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()


def edit_user(conn, username, new_password, new_email):
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET username = ?, password = ?, email = ?
                      WHERE username = ?''', (username, new_password, new_email, username))
    conn.commit()


def view_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password, email FROM users')
    users = cursor.fetchall()

    users_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'email': user[3]
        }
        users_list.append(user_dict)

    return users_list