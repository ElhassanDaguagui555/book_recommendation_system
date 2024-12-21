
#utils/borrowing.py

from datetime import datetime, timedelta

def borrow_book(conn, user_id, book_title):
    c = conn.cursor()
    
    # Vérifier si le livre existe et n'est pas déjà emprunté
    c.execute('SELECT id FROM books WHERE title = ? AND id NOT IN (SELECT book_id FROM loans WHERE return_date IS NULL)', (book_title,))
    book = c.fetchone()
    if not book:
        return False, "Ce livre n'est pas disponible pour l'emprunt."
    
    book_id = book[0]
    
    # Vérifier si l'utilisateur n'a pas dépassé la limite d'emprunts
    c.execute('SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL', (user_id,))
    current_loans = c.fetchone()[0]
    if current_loans >= 5:  # Limite arbitraire de 5 livres
        return False, "Vous avez atteint la limite maximale d'emprunts."
    
    # Effectuer l'emprunt
    loan_date = datetime.now().date()
    c.execute('INSERT INTO loans (user_id, book_id, loan_date) VALUES (?, ?, ?)',
              (user_id, book_id, loan_date))
    
    conn.commit()
    return True, f"Livre '{book_title}' emprunté avec succès. À retourner dans 30 jours."

def return_book(conn, user_id, book_title):
    c = conn.cursor()
    return_date = datetime.now().date()
    c.execute('''
        UPDATE loans 
        SET return_date = ? 
        WHERE user_id = ? AND book_id = (SELECT id FROM books WHERE title = ?) AND return_date IS NULL
    ''', (return_date, user_id, book_title))
    conn.commit()
    if c.rowcount > 0:
        return True, f"Livre '{book_title}' retourné avec succès."
    else:
        return False, f"Aucun emprunt en cours trouvé pour le livre '{book_title}'."

def get_user_loans(conn, user_id):
    c = conn.cursor()
    c.execute('''
        SELECT l.id, b.title, b.author, l.loan_date
        FROM loans l
        JOIN books b ON l.book_id = b.id
        WHERE l.user_id = ? AND l.return_date IS NULL
    ''', (user_id,))
    loans = c.fetchall()
    return [{'id': loan[0], 'title': loan[1], 'author': loan[2], 'loan_date': loan[3]}
            for loan in loans]