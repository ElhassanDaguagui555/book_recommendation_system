


#pages/recherche

import streamlit as st
import sqlite3
from utils.recommander import recommend_books

def app(conn):
    st.title("Recherche de livres")

    search_term = st.text_input("Entrez un terme de recherche")
    if st.button("Rechercher"):
        c = conn.cursor()
        c.execute("SELECT id, title, image FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?", 
                  ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
        results = c.fetchall()

        if results:
            for result in results:
                book_details = get_book_details(conn, result[0])
                show_book_details(book_details)

            # Recommandations basées sur le contenu
            st.markdown('<div class="sidebar"><h3>Livres similaires</h3></div>', unsafe_allow_html=True)
            content_recommendations = recommend_books(conn, st.session_state.user[0], num_recommendations=3, based_on_search=search_term)
            if content_recommendations:
                for book in content_recommendations:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(book['image'], width=100)
                    with col2:
                        st.write(f"**{book['title']}**")
                        st.write(book['description'][:100] + "...")
            else:
                st.write("Aucune recommandation similaire disponible.")
        else:
            st.write("Aucun résultat trouvé")

def get_book_details(conn, book_id):
    c = conn.cursor()
    c.execute("SELECT title, author, genre, published_date, description, image FROM books WHERE id = ?", (book_id,))
    return c.fetchone()

def show_book_details(book):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(book[5], width=100)
    with col2:
        st.write(f"**Titre** : {book[0]}")
        st.write(f"**Auteur** : {book[1]}")
        st.write(f"**Genre** : {book[2]}")
        st.write(f"**Date de publication** : {book[3]}")
        st.write(f"**Description** : {book[4]}")
        st.write("---")