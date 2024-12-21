

#utils/reviews.py

import sqlite3

def add_review(conn, user_id, book_id, rating, comment):
    c = conn.cursor()
    c.execute('INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (?, ?, ?, ?)', (user_id, book_id, rating, comment))
    conn.commit()