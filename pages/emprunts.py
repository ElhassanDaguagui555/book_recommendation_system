

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