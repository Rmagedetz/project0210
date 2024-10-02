import streamlit as st

import sql_queries

st.write("Страница с оплатами")
selected_season = st.session_state.get('selected_season', 'Сезон не выбран')

table = sql_queries.Payments.get_as_dataframe()
add_receipt_btn = st.button("Добавить приход", key="adding_receipt_open_dialog_btn")


@st.dialog("Добавление прихода")
def adding_receipt():
    col1, col2 = st.columns(2)
    with col1:
        parent_list = list(set(sql_queries.Children.get_parent_list()))
        parent_select = st.selectbox("Родитель", parent_list)
    with col2:
        child_list = list(set(sql_queries.Children.get_child_list_for_parent(parent_select)))
        child_select = st.selectbox("Ребенок", child_list)
    with col1:
        paytype = st.selectbox("Тип оплаты", ["Наличные", "Карта", "Терминал"])
    with col2:
        summa = st.number_input("Сумма")
    comment = st.text_area("Комментарий")
    if st.button("Добавить приход", key="adding_receipt_accept_btn"):
        login = st.session_state.user
        season = selected_season
        sql_queries.Payments.add_record(login=login,
                                        season=season,
                                        child_name=child_select,
                                        parent_name=parent_select,
                                        paytype=paytype,
                                        summa=summa,
                                        comment=comment)
        st.rerun()


if add_receipt_btn:
    adding_receipt()

st.write(table)