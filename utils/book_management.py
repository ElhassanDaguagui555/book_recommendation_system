

#utils/book_management

import sqlite3

def add_book(conn, title, author, genre, published_date, description, image):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO books (title, author, genre, published_date, description, image) 
                      VALUES (?, ?, ?, ?, ?, ?)''', (title, author, genre, published_date, description, image.read()))
    conn.commit()

def edit_book(conn, book_title, new_title, new_author, new_genre, new_published_date, new_description, new_image):
    cursor = conn.cursor()
    cursor.execute('''UPDATE books SET title = ?, author = ?, genre = ?, published_date = ?, description = ?, image = ?
                      WHERE title = ?''', (new_title, new_author, new_genre, new_published_date, new_description, new_image.read(), book_title))
    conn.commit()

def delete_book(conn, book_title):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE title = ?', (book_title,))
    conn.commit()

def view_books(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT title, author, genre, published_date, description, image FROM books')
    books = cursor.fetchall()

    books_list = []
    for book in books:
        book_dict = {
            'title': book[0],
            'author': book[1],
            'genre': book[2],
            'published_date': book[3],
            'description': book[4],
            'image': book[5]
        }
        books_list.append(book_dict)

    return books_list