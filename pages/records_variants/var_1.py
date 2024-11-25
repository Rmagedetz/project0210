import streamlit as st
import sql

user_logged = st.session_state.user
season = "Сезон 11"

groups_info = sql.get_groups_with_children_count_and_paid_by_season(season_name=season)


@st.dialog("Добавление ребенка в группу")
def add_child_to_group():
    addition_type = st.radio("Тип добавления", ["Жители городка", "Новый"])
    season = st.session_state.season
    filial = st.session_state.filial
    group = st.session_state.group
    if addition_type:
        if addition_type == "Жители городка":
            child_selector = st.selectbox("Ребенок", sql.get_children_list(), index=None)
            if st.button("Добавить"):
                sql.add_child_to_group(child_selector, season, filial, group)
                st.rerun()
        else:
            child_name = st.text_input("Имя ребенка")
            age = st.number_input("Возраст ребенка", min_value=0, step=1, value=0)
            parent_name = st.text_input("Родитель")
            parent_phone = st.text_input("Номер телефона")
            if st.button("Добавить"):
                child_data = {"name": child_name,
                              "age": age,
                              "parent_main_name": parent_name,
                              "parent_main_phone": parent_phone}
                success = sql.add_leaver(child_data)
                if success:
                    sql.add_child_to_group(child_name, season, filial, group)
                    st.rerun()
                else:
                    st.error("Ребенок с таким именем уже существует")


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


@st.dialog("Добавить группу в филиал")
def add_group_to_filial():
    season = st.session_state.selected_season
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


for filial, groups_list in groups_info.items():
    st.subheader(filial, divider=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    num_cols = 5

    last_filled_col = -1

    for i, group in enumerate(groups_list):
        col_idx = i % num_cols
        with cols[col_idx]:

            with st.container(border=True):
                if st.button(group, key=group):
                    st.session_state.season = season
                    st.session_state.filial = filial
                    st.session_state.group = group
                    st.switch_page("pages/group_cards/group_card.py")

                st.write(f"Мест: {groups_list[group]["capacity"]}")
                st.write(f"Бронь: {groups_list[group]["children_count"]}")
                st.write(f"Оплачено: {groups_list[group]["paid_children_count"]}")
                st.write(f"Осталось: {groups_list[group]["remaining_capacity"]}")
                if st.button(":material/group:", key=f"add_child_to{group}",
                             help=f"Добавить ребенка в {group}"):
                    st.session_state.season = season
                    st.session_state.filial = filial
                    st.session_state.group = group
                    add_child_to_group()

        last_filled_col = col_idx

    next_col = (last_filled_col + 1) % num_cols
    with cols[next_col]:
        if st.button(f'Добавить группу в {filial}'):
            st.session_state.selected_season = season
            st.session_state.filial_selected = filial
            add_group_to_filial()

st.divider()
if st.button("Добавить филиал"):
    st.session_state.selected_season = season
    add_filial()
