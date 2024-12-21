

#pages/avis
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