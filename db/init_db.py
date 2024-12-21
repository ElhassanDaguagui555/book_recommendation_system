#db/init_db.py

import sqlite3

def create_tables():
    conn = sqlite3.connect('db/library.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        genre TEXT,
        published_date DATE,
        description TEXT,
        image BLOB  
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        book_id INTEGER,
        loan_date DATE,
        return_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        book_id INTEGER,
        rating INTEGER,
        comment TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id),
        UNIQUE(user_id, book_id) ON CONFLICT REPLACE
    )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()