

#utils/notifications

import sqlite3
from datetime import datetime, timedelta

def get_overdue_loans(conn):
    c = conn.cursor()
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    c.execute('''
        SELECT l.id, u.id as user_id, u.username, b.title, l.loan_date
        FROM loans l
        JOIN users u ON l.user_id = u.id
        JOIN books b ON l.book_id = b.id
        WHERE l.return_date IS NULL AND l.loan_date <= ?
    ''', (thirty_days_ago,))
    loans = c.fetchall()
    return [{'id': loan[0], 'user_id': loan[1], 'username': loan[2], 'title': loan[3], 'loan_date': loan[4]}
            for loan in loans]

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_notification(user_email, book_title, due_date):
    message = Mail(
        from_email='hdagaugui@gmail.com',
        to_emails=user_email,
        subject=f'Rappel: Retour de livre - {book_title}',
        html_content=f'<p>Le livre "{book_title}" est à retourner avant le {due_date}.</p>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Notification envoyée à {user_email}")
    except Exception as e:
        print(str(e))