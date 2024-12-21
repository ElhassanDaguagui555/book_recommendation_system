

#pages/bibliothecaires

import streamlit as st
import pandas as pd
import sqlite3

def app(conn):
    st.title("Bibliothécaires")
    st.write("Page de gestion des bibliothécaires")

    # Créer la table des bibliothécaires si elle n'existe pas
    create_librarians_table(conn)

    # Tabs pour ajouter, modifier, supprimer et afficher
    tab1, tab2, tab3, tab4 = st.tabs(["Ajouter", "Modifier", "Supprimer", "Afficher"])

    with tab1:
        add_librarian(conn)

    with tab2:
        modify_librarian(conn)

    with tab3:
        delete_librarian(conn)

    with tab4:
        show_librarians(conn)

def create_librarians_table(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS librarians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()

def add_librarian(conn):
    st.subheader("Ajouter un bibliothécaire")

    with st.form("add_librarian_form"):
        name = st.text_input("Nom")
        email = st.text_input("Email")
        phone = st.text_input("Téléphone")
        submitted = st.form_submit_button("Ajouter")

        if submitted:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO librarians (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
                conn.commit()
                st.success("Bibliothécaire ajouté avec succès!")
            except sqlite3.IntegrityError:
                st.error("Un bibliothécaire avec cet email existe déjà.")

def modify_librarian(conn):
    st.subheader("Modifier un bibliothécaire")

    c = conn.cursor()
    c.execute("SELECT id, name FROM librarians")
    librarians = c.fetchall()
    librarian_dict = {name: id for id, name in librarians}
    
    selected_librarian = st.selectbox("Sélectionner un bibliothécaire à modifier", list(librarian_dict.keys()))

    if selected_librarian:
        librarian_id = librarian_dict[selected_librarian]

        with st.form("modify_librarian_form"):
            new_name = st.text_input("Nouveau nom", selected_librarian)
            new_email = st.text_input("Nouvel email")
            new_phone = st.text_input("Nouveau téléphone")
            submitted = st.form_submit_button("Modifier")

            if submitted:
                c.execute("UPDATE librarians SET name = ?, email = ?, phone = ? WHERE id = ?", (new_name, new_email, new_phone, librarian_id))
                conn.commit()
                st.success("Bibliothécaire modifié avec succès!")

def delete_librarian(conn):
    st.subheader("Supprimer un bibliothécaire")

    c = conn.cursor()
    c.execute("SELECT id, name FROM librarians")
    librarians = c.fetchall()
    librarian_dict = {name: id for id, name in librarians}

    selected_librarian = st.selectbox("Sélectionner un bibliothécaire à supprimer", list(librarian_dict.keys()))

    if selected_librarian:
        librarian_id = librarian_dict[selected_librarian]

        if st.button("Supprimer"):
            c.execute("DELETE FROM librarians WHERE id = ?", (librarian_id,))
            conn.commit()
            st.success("Bibliothécaire supprimé avec succès!")

def show_librarians(conn):
    st.subheader("Liste des bibliothécaires")

    c = conn.cursor()
    c.execute("SELECT id, name, email, phone FROM librarians")
    librarians = c.fetchall()

    df = pd.DataFrame(librarians, columns=["ID", "Nom", "Email", "Téléphone"])
    st.dataframe(df)