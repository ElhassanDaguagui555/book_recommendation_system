
#pages/reports.py

import streamlit as st
import pandas as pd
from utils.rapports import generate_borrowing_report, generate_overdue_report

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