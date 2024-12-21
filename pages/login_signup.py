

#pages/login_signup

import streamlit as st
from utils.auth import login, signup
from utils.db_utils import init_connection

def app():
    conn = init_connection()
    menu = ["Connexion", "Inscription"]
    choice = st.selectbox("Menu", menu)

    if choice == "Connexion":
        st.subheader("Connexion")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type='password')
        if st.button("Se connecter"):
            user = login(conn, username, password)
            if user:
                st.success(f"Bienvenue {user[1]}")
                st.session_state.logged_in = True
                st.session_state.user = user
                st.experimental_rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect")

    elif choice == "Inscription":
        st.subheader("Inscription")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type='password')
        email = st.text_input("Email")
        if st.button("S'inscrire"):
            signup(conn, username, password, email)
            st.success("Inscription réussie, vous pouvez maintenant vous connecter")
    conn.close()