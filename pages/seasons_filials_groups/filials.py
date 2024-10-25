import streamlit as st
import sql

user_logged = st.session_state.user
seasons = sql.get_seasons_list()
selected_season = st.selectbox("Сезон", seasons, index=None)


@st.dialog("Добавление филиала")
def add_filial():
    season = st.session_state.selected_season
    filial_name = st.text_input("Название филиала")
    if st.button("Добавить филиал", key="add_filial_accept"):
        if not filial_name:
            st.error("Введите название филиала")
        else:
            sql.add_filial(season, filial_name)
            st.rerun()


@st.dialog("Удаление филиала")
def delete_filial():
    season = st.session_state.selected_season
    fil_list = sql.get_filials_list_for_season(season)
    fil_selected = st.selectbox("Выберите филиал", fil_list, index=None)
    if fil_selected:
        if st.button("Удалить филиал", key="delete_filial_accept"):
            try:
                sql.delete_filial_from_season(season, fil_selected)
                st.rerun()
            except:
                st.error("Невозможно удалить филиал, так как в нем есть группы")


@st.dialog("Редактирование филиала")
def edit_filial():
    season = st.session_state.selected_season
    fil_list = sql.get_filials_list_for_season(season)
    fil_selected = st.selectbox("Выберите филиал", fil_list, index=None)
    if fil_selected:
        new_name = st.text_input("Новое имя филиала", fil_selected)
        if st.button("Редактировать филиал", key="edit_filial_accept"):
            sql.rename_filial(season, fil_selected, new_name)
            st.rerun()


if selected_season:
    st.session_state.selected_season = selected_season
    data = sql.show_filials_for_season(selected_season)
    st.write(data)
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            if st.button("Добавить филиал", key="add_filial",
                         disabled=not (sql.check_user_rights(user_logged, "adding_filials")),
                         use_container_width=True):
                add_filial()
            if st.button("Удалить филиал", key="delete_filial",
                         disabled=not (sql.check_user_rights(user_logged, "deleting_filials")),
                         use_container_width=True):
                delete_filial()
            if st.button("Переименовать филиал", key="rename_filial",
                         disabled=not (sql.check_user_rights(user_logged, "editing_filials")),
                         use_container_width=True):
                edit_filial()
