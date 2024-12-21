

#pages/notifications.py

import streamlit as st
from utils.notifications import get_overdue_loans, send_notification

def app(conn):
    st.title("Gestion des notifications")

    # Récupérer les emprunts en retard
    overdue_loans = get_overdue_loans(conn)

    if overdue_loans:
        st.subheader("Emprunts en retard")
        for loan in overdue_loans:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{loan['username']}** - {loan['title']}")
            with col2:
                # Vérifier que 'due_date' est présent dans les données
                due_date = loan.get('due_date', 'Non disponible')
                st.write(f"Date d'échéance: {due_date}")
            with col3:
                # Vérifier avant l'envoi
                if due_date != 'Non disponible' and st.button("Envoyer un rappel", key=f"notify_{loan['id']}"):
                    send_notification(loan['user_id'], loan['title'], due_date)
                    st.success("Notification envoyée")
    else:
        st.info("Aucun emprunt en retard.")

    # Envoyer des notifications pour tous les retards
    if st.button("Envoyer des notifications pour tous les retards"):
        for loan in overdue_loans:
            due_date = loan.get('due_date', None)
            if due_date:  # Vérifie que 'due_date' est valide
                send_notification(loan['user_id'], loan['title'], due_date)
        st.success("Toutes les notifications ont été envoyées")
