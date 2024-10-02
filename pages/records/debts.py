import streamlit as st
st.write("Страница со списаниями")
selected_season = st.session_state.get('selected_season', 'Сезон не выбран')
