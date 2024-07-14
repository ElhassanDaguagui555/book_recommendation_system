#db/init_db.py

import sqlite3

def create_tables():
    conn = sqlite3.connect('db/library.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        genre TEXT,
        published_date DATE,
        description TEXT,
        image BLOB  
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        book_id INTEGER,
        loan_date DATE,
        return_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        book_id INTEGER,
        rating INTEGER,
        comment TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id),
        UNIQUE(user_id, book_id) ON CONFLICT REPLACE
    )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
#pages/accueil
import streamlit as st
from utils.recommander import recommend_books
from datetime import datetime, timedelta

def app(conn):
    st.markdown("""
        <style>
        .big-font {
            font-size:30px !important;
            font-weight: bold;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #F0F2F6;
            border-radius: 5px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)

    # Message de bienvenue
    st.markdown('<p class="big-font">👋 Bienvenue, {}!</p>'.format(st.session_state.user[1]), unsafe_allow_html=True)

  

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📚 Recommandations pour vous", "📊 Statistiques", "🕰️ Activités récentes"])
    with tab1:
           # Barre de recherche
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("chercher un livre")
        with col2:
            st.write("  ")
            st.write("  ")
            if st.button("🔍 Rechercher"):
                search_results = perform_search(conn, search_term)
                if search_results:
                    with col1:
                        col3, col4 = st.columns([3, 1])
                        with col3:
                            st.subheader("Résultats de la recherche")
                            for book in search_results:
                                st.image(book['image'], width=100)
                        
                        with col4:
                            for book in search_results:
                                st.write(f"**{book['title']}**")
                                st.write(f"Auteur: {book['author']}")
                                st.write(book['description'][:100] + "...")
                else:
                    st.info("Aucun résultat trouvé") 
        st.subheader("📚 Recommandations pour vous")
        recommendations = recommend_books(conn, st.session_state.user[0], num_recommendations=5)
        if recommendations:
            cols = st.columns(5)
            for idx, book in enumerate(recommendations):
                with cols[idx]:
                    st.image(book['image'], width=100)
                    st.write(f"**{book['title'][:20]}...**")
        else:
            st.info("Aucune recommandation disponible pour le moment.") 
    with tab2:
        borrowed_books, due_soon = get_user_stats(conn, st.session_state.user[0])
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Livres empruntés", borrowed_books)
        with col2:
            st.metric("À rendre bientôt", due_soon)

    with tab3:
        activities = get_recent_activities(conn, st.session_state.user[0])
        for activity in activities:
            title, loan_date, return_date = activity
            loan_date_formatted = format_date(loan_date)
            if return_date:
                return_date_formatted = format_date(return_date)
                st.write(f"- Rendu : '{title}' le {return_date_formatted}")
            else:
                st.write(f"- Emprunté : '{title}' le {loan_date_formatted}")

    

def perform_search(conn, search_term):
    c = conn.cursor()
    c.execute("""
    SELECT id, title, author, description, image 
    FROM books 
    WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
    """, ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
    results = c.fetchall()
    return [{"id": r[0], "title": r[1], "author": r[2], "description": r[3], "image": r[4]} for r in results]

def get_user_stats(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL", (user_id,))
    borrowed_books = c.fetchone()[0]
    
    due_date = datetime.now() + timedelta(days=7)
    c.execute("SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL AND loan_date <= ?", (user_id, due_date))
    due_soon = c.fetchone()[0]
    
    return borrowed_books, due_soon

def get_recent_activities(conn, user_id):
    c = conn.cursor()
    c.execute("""
    SELECT books.title, loans.loan_date, loans.return_date                                                  
    FROM loans 
    JOIN books ON loans.book_id = books.id 
    WHERE loans.user_id = ? 
    ORDER BY COALESCE(loans.return_date, loans.loan_date) DESC 
    LIMIT 5
    """, (user_id,))
    return c.fetchall()

def format_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return date_str
    return "Date inconnue"

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

#page/avis
import streamlit as st
from utils.reviews import add_review

def app(conn):
    st.title("Avis et notes")

    # Initialisation
    user = st.session_state.get('user')
    user_id = user[0]
    c = conn.cursor()
    c.execute("SELECT id, title FROM books ORDER BY title")
    books = c.fetchall()
    book_options = {title: id for id, title in books}

    # Onglets
    tab1, tab2 = st.tabs(["Ajouter un avis", "Voir les avis"])

    with tab1:
        st.header("Ajouter un avis")
        st.write("Remplissez les informations ci-dessous pour ajouter votre avis.")

        selected_book_title = st.selectbox("Sélectionner un livre", list(book_options.keys()))
        book_id = book_options[selected_book_title]

        rating = st.slider("Note", 1, 5)
        comment = st.text_area("Commentaire")

        if st.button("Ajouter un avis"):
            add_review(conn, user_id, book_id, rating, comment)
            st.success("Avis ajouté avec succès")

    with tab2:
        st.header("Voir les avis")
        st.write("Sélectionner un livre pour voir les avis déjà ajoutés.")

        selected_book_title_reviews = st.selectbox("Sélectionner un livre", list(book_options.keys()), key="view_reviews")
        
        if st.button("Voir avis", key="view_reviews_button"):
            book_id = book_options[selected_book_title_reviews]
            c.execute("SELECT * FROM reviews WHERE id = ?", (book_id,))
            reviews = c.fetchall()

            if reviews:
                st.subheader(f"Avis pour {selected_book_title_reviews}:")
                for review in reviews:
                    with st.expander(f"Avis de l'utilisateur {review[1]}"):
                        st.write(f"Note : {'⭐' * review[3]}")
                        st.write(f"Commentaire : {review[4]}")
            else:
                st.info("Aucun avis trouvé pour ce livre")

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

#pages/emprunts.py

import streamlit as st
from datetime import datetime, timedelta
from utils.borrowing import borrow_book, return_book, get_user_loans

def app(conn):
    st.title("Gestion des emprunts")

    user = st.session_state.get('user')
    user_id = user[0]

    tab1, tab2 = st.tabs(["Mes emprunts", "Emprunter un livre"])

    with tab1:
        st.subheader("Mes emprunts en cours")
        loans = get_user_loans(conn, user_id)
        
        if loans:
            for loan in loans:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{loan['title']}** par {loan['author']}")
                with col2:
                    loan_date = datetime.strptime(loan['loan_date'], '%Y-%m-%d')
                    due_date = loan_date + timedelta(days=30)
                    st.write(f"Emprunté le: {loan_date.strftime('%d/%m/%Y')}")
                    st.write(f"À retourner avant le: {due_date.strftime('%d/%m/%Y')}")
                with col3:
                    if st.button("Retourner", key=f"return_{loan['id']}"):
                        success, message = return_book(conn, user_id, loan['title'])
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                        st.experimental_rerun()
                st.markdown("---")
        else:
            st.info("Vous n'avez aucun emprunt en cours.")

    with tab2:
        st.subheader("Emprunter un nouveau livre")
        book_title = st.text_input("Titre du livre")
        if st.button("Emprunter"):
            success, message = borrow_book(conn, user_id, book_title)
            if success:
                st.success(message)
            else:
                st.error(message)

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

#pages/notifications.py

import streamlit as st
from utils.notifications import get_overdue_loans, send_notification

def app(conn):
    st.title("Gestion des notifications")

    overdue_loans = get_overdue_loans(conn)

    if overdue_loans:
        st.subheader("Emprunts en retard")
        for loan in overdue_loans:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{loan['username']}** - {loan['title']}")
            with col2:
                st.write(f"Date d'échéance: {loan['due_date']}")
            with col3:
                if st.button("Envoyer un rappel", key=f"notify_{loan['id']}"):
                    send_notification(loan['user_id'], loan['title'], loan['due_date'])
                    st.success("Notification envoyée")
    else:
        st.info("Aucun emprunt en retard.")

    if st.button("Envoyer des notifications pour tous les retards"):
        for loan in overdue_loans:
            send_notification(loan['user_id'], loan['title'], loan['due_date'])
        st.success("Toutes les notifications ont été envoyées")

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

#pages/reports.py

import streamlit as st
import pandas as pd
from utils.reports import generate_borrowing_report, generate_overdue_report

def app(conn):
    st.title("Rapports de la bibliothèque")

    tab1, tab2 = st.tabs(["Emprunts en cours", "Retards"])

    with tab1:
        st.subheader("Rapport des emprunts en cours")
        df_current = generate_borrowing_report(conn)
        if not df_current.empty:
            st.dataframe(df_current)
            csv = df_current.to_csv(index=False)
            st.download_button(
                label="Télécharger le rapport (CSV)",
                data=csv,
                file_name="emprunts_en_cours.csv",
                mime="text/csv",
            )
        else:
            st.info("Aucun emprunt en cours.")

    with tab2:
        st.subheader("Rapport des retards")
        df_overdue = generate_overdue_report(conn)
        if not df_overdue.empty:
            st.dataframe(df_overdue)
            csv = df_overdue.to_csv(index=False)
            st.download_button(
                label="Télécharger le rapport (CSV)",
                data=csv,
                file_name="emprunts_en_retard.csv",
                mime="text/csv",
            )
        else:
            st.info("Aucun emprunt en retard.")

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

#pages/recommendations

import streamlit as st
from utils.recommander import recommend_books

def app(conn):
    st.title("Recommandations de livres")
    user = st.session_state.get('user')

    if user:
        st.subheader(f"Recommandations pour {user[1]}")
        recommended_books = recommend_books(conn, user[0])  # Utilisez la fonction de recommandation

        if recommended_books:
            for i in range(0, len(recommended_books), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(recommended_books):
                        book = recommended_books[i + j]
                        with col:
                            
                            st.image(book['image'], width=100)
                            
                            st.write(f"**{book['title']}**")
                            if st.button("Voir plus", key=book['id']):
                                st.session_state['selected_book'] = book['id']
                                st.experimental_rerun()
        else:
            st.write("Aucune recommandation disponible pour l'instant.")
    else:
        st.write("Veuillez vous connecter pour voir les recommandations.")

#utils/auth.py

import sqlite3

def login(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    return user

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


def delete_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()


def edit_user(conn, username, new_password, new_email):
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET username = ?, password = ?, email = ?
                      WHERE username = ?''', (username, new_password, new_email, username))
    conn.commit()


def view_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password, email FROM users')
    users = cursor.fetchall()

    users_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'email': user[3]
        }
        users_list.append(user_dict)

    return users_list

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

#utils/categorisations.py

import sqlite3

def categorize_books(conn):
    c = conn.cursor()
    c.execute('SELECT genre, COUNT(*) FROM books GROUP BY genre')
    return c.fetchall()
#utils/db_utils
import sqlite3

def init_connection():
    return sqlite3.connect('db/library.db')

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

#utils/recommander

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def load_data(conn):
    query = "SELECT id, title, image, description FROM books"
    df = pd.read_sql_query(query, conn)
    if df.empty:
        print("No books found in the database.")
    return df

def train_model(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['description'].fillna(''))
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def recommend_books(conn, user_id, num_recommendations=5, based_on_search=None):
    df = load_data(conn)
    if df.empty:
        return []
    
    cosine_sim = train_model(df)
    
    if based_on_search:
        # Recommandations basées sur la recherche
        idx = df[df['title'].str.contains(based_on_search, case=False) |
                 df['author'].str.contains(based_on_search, case=False) |
                 df['genre'].str.contains(based_on_search, case=False)].index
    else:
        # Recommandations basées sur le dernier livre emprunté
        last_book_id = get_last_borrowed_book_id(conn, user_id)
        if last_book_id is None:
            return []
        idx = df[df['id'] == last_book_id].index
    
    if len(idx) == 0:
        return []
    idx = idx[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations+1]
    
    book_indices = [i[0] for i in sim_scores]
    return df.iloc[book_indices].to_dict('records')

def get_last_borrowed_book_id(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT book_id FROM loans WHERE user_id = ? ORDER BY loan_date DESC LIMIT 1", (user_id,))
    last_book = c.fetchone()
    if last_book:
        return last_book[0]
    else:
        return None

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

#utils/reviews.py

import sqlite3

def add_review(conn, user_id, book_id, rating, comment):
    c = conn.cursor()
    c.execute('INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (?, ?, ?, ?)', (user_id, book_id, rating, comment))
    conn.commit()

#app.py

import streamlit as st
from streamlit_option_menu import option_menu
from utils.db_utils import init_connection
from pages import accueil, emprunts, profil, avis, bibliothecaires, notifications, rapports
from pages import auth, admin, recommendations

st.set_page_config(layout="wide", page_title="Application de Bibliothèque")
st.markdown(
    """
    <style>
    .header {
        background-color: gray;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .sidebar {
        background-color: orange;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .footer {
        background-color: lime;
        margin-top: 20px;
        padding-top: 10px;
        border-top: 1px solid #ccc;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialisation de la connexion à la base de données
conn = init_connection()

# Créer la table des utilisateurs si elle n'existe pas
auth.create_user_table(conn)

# Vérifier si l'utilisateur est authentifié
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Afficher la page de connexion/inscription si l'utilisateur n'est pas authentifié
    auth.auth_page(conn)
elif st.session_state.get('admin', False):
    # Afficher l'interface administrateur si l'utilisateur est l'administrateur
    admin.app(conn)
else:
    # En-tête
    st.markdown("""
        <div class="main-header">
            <h1><img src="https://c8.alamy.com/compfr/2j7fk37/icone-de-livre-empile-symbole-de-bibliotheque-logo-de-la-librairie-2j7fk37.jpg" width=100> Application de Bibliothèque📚</h1>
        </div>
    """, unsafe_allow_html=True)

    # Menu de navigation
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=["Accueil", "Emprunts", "Profil", "Avis", "Bibliothécaires", "Notifications", "Rapports", "Recommandations", "Déconnexion"],
            icons=['house', 'book', 'person', 'chat', 'people', 'bell', 'graph-up', 'star', 'box-arrow-right'],
            menu_icon="cast",
            default_index=0,
        )

    # Contenu principal
    st.markdown('<div class="content">', unsafe_allow_html=True)
    pages = {
        "Accueil": accueil,
        "Emprunts": emprunts,
        "Profil": profil,
        "Avis": avis,
        "Bibliothécaires": bibliothecaires,
        "Notifications": notifications,
        "Rapports": rapports,
        "Recommandations": recommendations
    }

    if selected in pages:
        pages[selected].app(conn)
    elif selected == "Déconnexion":
        st.session_state.authenticated = False
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Pied de page
    st.markdown('<div class="footer">© 2024 Bibliothèque App</div>', unsafe_allow_html=True)

# Fermer la connexion à la base de données
conn.close()

#recommander.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def load_data(conn):
    query = "SELECT id, title, description FROM books"
    df = pd.read_sql_query(query, conn)
    return df

def train_model(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['description'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def recommend_books(conn, user_id, num_recommendations=5):
    df = load_data(conn)
    if df.empty:
        return []
    
    cosine_sim = train_model(df)
    
    last_book_id = get_last_borrowed_book_id(conn, user_id)
    if last_book_id is None:
        return []
    
    idx = df[df['id'] == last_book_id].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations+1]
    
    book_indices = [i[0] for i in sim_scores]
    return df.iloc[book_indices].to_dict('records')

def get_last_borrowed_book_id(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT book_id FROM loans WHERE user_id = ? ORDER BY loan_date DESC LIMIT 1", (user_id,))
    last_book = c.fetchone()
    if last_book:
        return last_book[0]
    else:
        return None
