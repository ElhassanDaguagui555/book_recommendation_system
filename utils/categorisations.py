

#utils/categorisations.py

import sqlite3

def categorize_books(conn):
    c = conn.cursor()
    c.execute('SELECT genre, COUNT(*) FROM books GROUP BY genre')
    return c.fetchall()
