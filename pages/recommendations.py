

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