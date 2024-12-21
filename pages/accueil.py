
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