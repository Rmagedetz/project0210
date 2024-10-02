import streamlit as st
import sql_queries
selected_season = st.session_state.get('selected_season', 'Сезон не выбран')

parent_list = sql_queries.Children.get_parent_list()
parent_selector = st.selectbox("Родитель", parent_list)

payments = sql_queries.Payments.get_as_dataframe_for_single_adult(parent_selector)
st.write(payments)