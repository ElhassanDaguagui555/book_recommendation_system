

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
