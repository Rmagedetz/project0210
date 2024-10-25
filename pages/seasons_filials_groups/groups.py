import streamlit as st
import sql

user_logged = st.session_state.user


@st.dialog("Добавить группу в филиал")
def add_group_to_filial():
    season = st.session_state.season_selected
    filial = st.session_state.filial_selected
    group_name = st.text_input("Название группы")
    start_date = st.date_input("Дата начала")
    end_date = st.date_input("Дата окончания")
    capacity = st.number_input("Количество детей", step=1, min_value=1)

    if st.button("Добавить группу в филиал", key="add_group_to_filial_accept"):
        success = sql.add_group_to_filial_in_season(season_name=season,
                                                    filial_name=filial,
                                                    group_data={"name": group_name,
                                                                "capacity": capacity,
                                                                "start_date": start_date,
                                                                "end_date": end_date})
        if success:
            st.rerun()
        else:
            st.error(f"Группа с названием '{group_name}' уже существует в филиале '{filial}'.")


@st.dialog("Удаление группы из филиала")
def delete_group_from_filial():
    season = st.session_state.season_selected
    filial = st.session_state.filial_selected
    group_list = sql.get_groups_list_for_filial_in_season(season, filial)
    group_selector = st.selectbox("Группа", group_list, index=None)
    if group_selector:
        if st.button("Удалить группу", key="delete_group_accept"):
            sql.delete_group_from_filial_in_season(season, filial, group_selector)
            st.rerun()


@st.dialog("Редактирование группы")
def edit_group():
    season = st.session_state.season_selected
    filial = st.session_state.filial_selected
    group_list = sql.get_groups_list_for_filial_in_season(season, filial)
    group_selector = st.selectbox("Группа", group_list, index=None)
    if group_selector:
        new_name = st.text_input("Название группы", group_selector)
        data = groups[groups["name"] == group_selector].reset_index()
        new_capacity = st.number_input("Количество детей", step=1, value=data["capacity"][0])
        new_start_date = st.date_input("Дата начала", value=data["start_date"][0], key="start")
        new_end_date = st.date_input("Дата начала", value=data["end_date"][0], key="end")
        if st.button("Редактировать данные группы", key="edit_group_data_accept"):
            success = sql.edit_group_data_in_filial_season(season_name=season,
                                                           filial_name=filial,
                                                           group_name=group_selector,
                                                           new_group_data={'name': new_name,
                                                                           'capacity': new_capacity,
                                                                           'start_date': new_start_date,
                                                                           'end_date': new_end_date
                                                                           })
            if success:
                st.rerun()
            else:
                st.error(f"Группа с названием '{new_name}' уже существует в филиале '{filial}'.")


season_selector = st.selectbox("Сезон", sql.get_seasons_list(), index=None, key="season_selector")
if season_selector:
    filial_selector = st.selectbox("Филиал", sql.get_filials_list_for_season(season_selector), index=None, key="fil_sel")
    if filial_selector:
        groups = sql.get_groups_dataframe_for_filial_in_season(season_selector, filial_selector)
        st.write(groups)
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                if st.button("Добавить группу в филиал", key="add_group_to_filial_btn",
                             disabled=not (sql.check_user_rights(user_logged, "adding_groups")),
                             use_container_width=True):
                    st.session_state.season_selected = season_selector
                    st.session_state.filial_selected = filial_selector
                    add_group_to_filial()
                if st.button("Удалить группу из филиала", key="delete_group_from_filial",
                             disabled=not (sql.check_user_rights(user_logged, "deleting_groups")),
                             use_container_width=True):
                    st.session_state.season_selected = season_selector
                    st.session_state.filial_selected = filial_selector
                    delete_group_from_filial()
                if st.button("Редактировать группу", key="edit_group",
                             disabled=not (sql.check_user_rights(user_logged, "editing_groups")),
                             use_container_width=True):
                    st.session_state.season_selected = season_selector
                    st.session_state.filial_selected = filial_selector
                    edit_group()

