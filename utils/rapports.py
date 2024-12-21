


#utils/reports.py

import pandas as pd
from datetime import datetime, timedelta

def generate_borrowing_report(conn):
    query = '''
    SELECT u.username, b.title, l.loan_date
    FROM loans l
    JOIN users u ON l.user_id = u.id
    JOIN books b ON l.book_id = b.id
    WHERE l.return_date IS NULL
    ORDER BY l.loan_date
    '''
    df = pd.read_sql_query(query, conn)
    df['loan_date'] = pd.to_datetime(df['loan_date'])
    df['due_date'] = df['loan_date'] + timedelta(days=30)
    df['loan_date'] = df['loan_date'].dt.strftime('%d/%m/%Y')
    df['due_date'] = df['due_date'].dt.strftime('%d/%m/%Y')
    return df

def generate_overdue_report(conn):
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    query = f'''
    SELECT u.username, b.title, l.loan_date
    FROM loans l
    JOIN users u ON l.user_id = u.id
    JOIN books b ON l.book_id = b.id
    WHERE l.return_date IS NULL AND l.loan_date <= '{thirty_days_ago}'
    ORDER BY l.loan_date
    '''
    df = pd.read_sql_query(query, conn)
    df['loan_date'] = pd.to_datetime(df['loan_date'])
    df['due_date'] = df['loan_date'] + timedelta(days=30)
    df['loan_date'] = df['loan_date'].dt.strftime('%d/%m/%Y')
    df['due_date'] = df['due_date'].dt.strftime('%d/%m/%Y')
    return df