

#pages/admin.py

import streamlit as st
from utils.book_management import add_book, edit_book, delete_book, view_books
from utils.auth import signup, delete_user, edit_user, view_users

def app(conn):
    st.title("Page d'administration")

    menu = ["Gérer les livres", "Gérer les utilisateurs", "Déconnexion"]
    choice = st.selectbox("Action", menu)

    if choice == "Gérer les livres":
        st.subheader("Gérer les livres")
        tabs = st.tabs(["Ajouter", "Modifier", "Supprimer", "Afficher"])

        with tabs[0]:
            st.subheader("Ajouter un nouveau livre")
            title = st.text_input("Titre")
            author = st.text_input("Auteur")
            genre = st.text_input("Genre")
            published_date = st.date_input("Date de publication")
            description = st.text_area("Description")
            image = st.file_uploader("Télécharger l'image", type=["jpg", "jpeg", "png"])
            if st.button("Ajouter"):
                add_book(conn, title, author, genre, published_date, description, image)
                st.success("Livre ajouté avec succès")

        with tabs[1]:
            st.subheader("Modifier un livre existant")
            book_title = st.text_input("Titre du livre à modifier")
            new_title = st.text_input("Nouveau titre")
            new_author = st.text_input("Nouvel auteur")
            new_genre = st.text_input("Nouveau genre")
            new_published_date = st.date_input("Nouvelle date de publication")
            new_description = st.text_area("Nouvelle description")
            new_image = st.file_uploader("Télécharger la nouvelle image", type=["jpg", "jpeg", "png"])
            if st.button("Modifier"):
                edit_book(conn, book_title, new_title, new_author, new_genre, new_published_date, new_description, new_image)
                st.success("Livre modifié avec succès")

        with tabs[2]:
            st.subheader("Supprimer un livre")
            book_title = st.text_input("Titre du livre à supprimer")
            if st.button("Supprimer"):
                delete_book(conn, book_title)
                st.success("Livre supprimé avec succès")

        with tabs[3]:
            st.subheader("Afficher les livres")
            books = view_books(conn)
            for book in books:
                col1, col2 = st.columns([1, 3])  # Division en colonnes (1 pour l'image, 3 pour les infos)

                with col1:
                    st.image(book['image'], width=100)  # Affiche l'image du livre avec une taille réduite

                with col2:
                    st.write(f"Titre: {book['title']}")
                    st.write(f"Auteur: {book['author']}")
                    st.write(f"Genre: {book['genre']}")
                    st.write(f"Date de publication: {book['published_date']}")
                    st.write(f"Description: {book['description']}")
                    st.write("---")  # Séparateur visuel entre chaque livre

    elif choice == "Gérer les utilisateurs":
        st.subheader("Gestion des utilisateurs")
        tabs = st.tabs(["Ajouter", "Modifier", "Supprimer", "Afficher"])

        with tabs[0]:
            st.subheader("Ajouter un utilisateur")
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type='password')
            email = st.text_input("Email")
            if st.button("Ajouter"):
                signup(conn, username, password, email)
                st.success("Utilisateur ajouté avec succès")

        with tabs[1]:
            st.subheader("Modifier un utilisateur")
          
            new_username = st.text_input("Nouveau nom d'utilisateur")
            new_password = st.text_input("Nouveau mot de passe", type='password')
            new_email = st.text_input("Nouvel email")
            if st.button("Modifier"):
                edit_user(conn, new_username, new_password, new_email)
                st.success("Utilisateur modifié avec succès")

        with tabs[2]:
            st.subheader("Supprimer un utilisateur")
            user_id = st.number_input("ID de l'utilisateur")
            if st.button("Supprimer"):
                delete_user(conn, user_id)
                st.success("Utilisateur supprimé avec succès")

        with tabs[3]:
            st.subheader("Afficher les utilisateurs")
            users = view_users(conn)
            for user in users:
                st.write(f"ID: {user['id']}")
                st.write(f"USERNAME: {user['username']}")
                st.write(f"PASSWORD: {user['password']}")
                st.write(f"EMAIL: {user['email']}")
                st.write("---")

    elif choice == "Déconnexion":
        st.session_state.authenticated = False
        st.experimental_rerun()
        