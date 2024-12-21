
# pages/auth.py

import streamlit as st
import sqlite3

def login(conn, username, password):
    if username == "hassan" and password == "hassan":
        return ("admin", "hassan", "hassan", "admin@example.com")  # Admin tuple
    else:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        return c.fetchone()

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

def auth_page(conn):
    st.title("Authentification")

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        st.header("Connexion")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            user = login(conn, username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                if user[0] == "admin":
                    st.session_state.admin = True
                else:
                    st.session_state.admin = False
                st.success("Connexion réussie!")
                st.experimental_rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

    with tab2:
        st.header("Inscription")
        new_username = st.text_input("Nouveau nom d'utilisateur")
        new_password = st.text_input("Nouveau mot de passe", type="password")
        new_email = st.text_input("Email")
        if st.button("S'inscrire"):
            if signup(conn, new_username, new_password, new_email):
                st.success("Inscription réussie! Veuillez vous connecter.")
            else:
                st.error("Ce nom d'utilisateur existe déjà.")