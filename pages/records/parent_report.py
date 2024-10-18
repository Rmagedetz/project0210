import streamlit as st
import sql_queries
selected_season = st.session_state.get('selected_season', 'Сезон не выбран')

parent_list = sql_queries.get_parent_list()
parent_selector = st.selectbox("Родитель", parent_list, index=None)

payments = sql_queries.get_payments_for_single_adult(parent_selector)
st.write(payments)