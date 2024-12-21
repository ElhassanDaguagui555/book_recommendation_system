
#pages/profil.py

import streamlit as st
from utils.auth import login


def app(conn):
    st.title("Profil")
    st.write("Page de gestion du profil utilisateur")
    user = st.session_state.get('user')
    
    
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user[0],))
    user = c.fetchone()

    if user:
        st.write(f"ID : {user[0]}")
        st.write(f"Nom d'utilisateur : {user[1]}")
        st.write(f"Email : {user[3]}")
    else:
        st.write("Utilisateur non trouvé")