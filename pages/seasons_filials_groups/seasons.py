import streamlit as st
import sql

user_logged = st.session_state.user

seasons = sql.get_seasons_dataframe()
st.write(seasons)


@st.dialog("Добавление сезона")
def adding_season():
    season_name = st.text_input("Название сезона:")
    start = st.date_input("Дата начала:")
    end = st.date_input("Дата окончания:")
    if st.button("Добавить сезон"):
        sql.add_season(season_name, start, end)
        st.rerun()


@st.dialog("Удаление сезона")
def deleting_season():
    season_selected = st.selectbox("Сезон", sql.get_seasons_list(), index=None)
    if st.button("Удалить сезон"):
        try:
            sql.delete_season(season_selected)
            st.success(f"Сезон '{season_selected}' успешно удален.")
            st.rerun()
        except Exception as e:
            st.error("Сезон удалить нельзя, так как он содержит филиалы.")


@st.dialog("Редактирование сезона")
def editing_season():
    seas = sql.get_seasons_dataframe()
    selected = st.selectbox("Сезон", sql.get_seasons_list(), index=None)
    if selected:
        data = seas[seas["name"] == selected].reset_index()
        new_name = st.text_input("Новое название", data["name"][0])
        new_start = st.date_input("Новая дата начала", data["start_date"][0])
        new_end = st.date_input("Новая дата окончания", data["end_date"][0])
        if st.button("Изменить сезон"):
            sql.update_season(selected, new_data={"name": new_name,
                                                  "start_date": new_start,
                                                  "end_date": new_end})
            st.rerun()


col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        if st.button("Добавить сезон", key="add_season_btn",
                     disabled=not (sql.check_user_rights(user_logged, "adding_seasons")),
                     use_container_width=True):
            adding_season()
        if st.button("Удалить сезон", key="delete_season_btn",
                     disabled=not (sql.check_user_rights(user_logged, "deleting_seasons")),
                     use_container_width=True):
            deleting_season()
        if st.button("Редактировать сезон", key="edit_season_btn",
                     disabled=not (sql.check_user_rights(user_logged, "editing_seasons")),
                     use_container_width=True):
            editing_season()
