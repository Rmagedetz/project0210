import streamlit as st
import sql_queries
from datetime import datetime

season_selected = st.sidebar.selectbox("Сезон", sql_queries.get_season_list())
st.session_state.season_selected = season_selected
season_id = sql_queries.get_season_id_by_name(season_selected)
st.session_state.selected_season_id = season_id


@st.dialog("Добавление сезона")
def add_season():
    season_name = st.text_input("Название сезона")
    season_start_date = st.date_input("Дата начала сезона")
    season_end_date = st.date_input("Дата окончания сезона")
    if st.button("Добавить сезон"):
        existing_seasons = sql_queries.get_season_list()
        if season_name in existing_seasons:
            st.error("Сезон с таким названием уже существует")
        else:
            sql_queries.add_season(season_name=season_name,
                                   start_date=season_start_date,
                                   end_date=season_end_date)
            st.rerun()


@st.dialog("Переименование сезона")
def update_season():
    selected_season_id = st.session_state.selected_season_id
    new_season_name = st.text_input("Новое название сезона")
    current_season_data = sql_queries.get_season_data_by_id(selected_season_id)
    new_season_start_date = st.date_input("Новая дата начала", current_season_data["season_start_date"])
    new_season_end_date = st.date_input("Новая дата окончания", current_season_data["season_end_date"])
    if st.button("Редактировать сезон"):
        if new_season_name == "":
            st.error("Введите имя сезона")
        else:
            existing_seasons = sql_queries.get_season_list()
            if new_season_name in existing_seasons:
                st.error("Сезон с таким названием уже существует")
            else:
                sql_queries.update_season(selected_season_id, new_data={"season_name": new_season_name,
                                                                        "season_start_date": new_season_start_date,
                                                                        "season_end_date": new_season_end_date})
                st.rerun()


@st.dialog("Добавление филиала")
def add_filial():
    selected_season_id = st.session_state.selected_season_id
    fil_name = st.text_input("Название филиала")
    if st.button("Добавить филиал"):
        if fil_name == "":
            st.error("Введите название филиала")
        else:
            existing_filials_in_season = sql_queries.get_filials_list_for_season(selected_season_id)
            if fil_name in existing_filials_in_season:
                st.error("Филиал с таким именем уже существует в выбраном сезоне")
            else:
                sql_queries.add_filial(filial_name=fil_name, season_id=selected_season_id)
                st.rerun()


if st.sidebar.button(":material/add_box:", key="add_season", help="Добавить сезон"):
    add_season()

if st.sidebar.button(":material/edit:", key="edit_season", help="Редактировать сезон"):
    update_season()


@st.dialog("Добавление группы в филиал")
def add_group_to_filial():
    selected_season_id = st.session_state.selected_season_id
    season_name = sql_queries.get_season_name_by_id(season_id=selected_season_id)
    selected_filial_id = st.session_state.filial_id
    filial_name = sql_queries.get_filial_name_by_id(filial_id=selected_filial_id)
    st.write(season_name, filial_name)
    new_group_name = st.text_input("Название группы")
    start = st.date_input("Начало")
    end = st.date_input("Конец")
    count = st.number_input("Емкость", step=1)
    if st.button("Добавить"):
        existing = sql_queries.get_groups_list_for_season_and_filial(selected_season_id, selected_filial_id)
        if new_group_name in existing:
            st.error("Группа с таким названием уже существует в филиале")
        else:
            sql_queries.add_group_to_filial_in_season(group_name=new_group_name,
                                                      group_size=count,
                                                      start_date=start,
                                                      end_date=end,
                                                      season_id=selected_season_id,
                                                      filial_id=selected_filial_id)
            st.rerun()


@st.dialog("Переименование филиала")
def rename_filial():
    selected_season_id = st.session_state.selected_season_id
    selected_filial_id = st.session_state.rename_filial
    fil_name = st.text_input("Новое название филиала")
    if st.button("Переименовать филиал"):
        if fil_name == "":
            st.error("Введите название филиала")
        else:
            existing_filials_in_season = sql_queries.get_filials_list_for_season(selected_season_id)
            if fil_name in existing_filials_in_season:
                st.error("Филиал с таким именем уже существует в выбраном сезоне")
            else:
                sql_queries.update_filial(filial_id=selected_filial_id, new_data={"filial_name": fil_name})
                st.rerun()


@st.dialog("Добавление ребенка в группу")
def add_child_to_group():
    season_id = st.session_state.selected_season_id
    filial_name = st.session_state.adding_child_filial_name
    group_name = st.session_state.adding_child_group_name
    filial_id = sql_queries.get_filial_id_by_name_and_season(filial_name=filial_name, season_id=season_id)
    group_id = sql_queries.get_group_id(season_id=season_id, filial_id=filial_id, group_name=group_name)

    addition_option_selector = st.selectbox("Тип добавления", ["Новый", "Из анкеты"])
    if addition_option_selector == "Новый":
        with st.container(border=True):
            child = st.text_input("ФИО ребенка")
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Возраст", step=1)
            with col2:
                phonenum = st.text_input("Номер телефона")

        with st.container(border=True):
            parent_list = [1, 2, 3, 4, 5]
            not_in_list = st.checkbox("Родителя нет в списке")
            if not_in_list:
                parent_input = st.text_input("Добавить родителя")
            else:
                parent_input = st.selectbox("ФИО родителя из списка", parent_list)

        if st.button("Добавить запись"):
            # Проверяем наличие актуальных данных
            if filial and group and child and age and parent_input:
                sql_queries.add_child(child_name=child,
                                      child_age=age,
                                      parent_name=parent_input,
                                      parent_num=phonenum,
                                      filial_id=filial_id,
                                      group_id=group_id,
                                      season_id=season_id)
                st.rerun()
            else:
                st.error("Проверьте заполненные данные")
    else:
        # Логика для добавления из анкеты
        child_list = sql_queries.get_info_list()
        child_selector = st.selectbox("Выберите ребенка", child_list, index=None)
        try:
            data = sql_queries.get_info_for_group_addition(child_selector)
            birthday, parent, phonenum = data
            age = calculate_age(birthday)
        except:
            pass
        if st.button("Добавить запись"):
            sql_queries.add_child(child_name=child_selector,
                                  child_age=age,
                                  parent_name=parent,
                                  parent_num=phonenum,
                                  filial_id=filial_id,
                                  group_id=group_id,
                                  season_id=season_id)
            st.success("Ребенок успешно добавлен в группу")
            st.rerun()


records_info = sql_queries.get_filials_groups_data_for_season(st.session_state.selected_season_id)

for filial, groups_list in records_info.items():
    st.subheader(filial, divider="blue")
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    num_cols = 5

    # Переменная для отслеживания последнего заполненного столбца
    last_filled_col = -1

    for i, group in enumerate(groups_list):
        col_idx = i % num_cols
        with cols[col_idx]:
            with st.container(border=True):
                group_name = group
                info = records_info[filial][group]
                free_places = info["group_size"] - info["children_recorded"]

                st.write(f"{group_name}: {free_places}")
                st.write(f"Бронь: {info['children_recorded']}")
                st.write(f"Оплачено: {info['children_payed']}")
                selected_season_id = st.session_state.selected_season_id
                group_id = 0
                if st.button(":material/add_box:", key=f"add_child_to{filial}{group}",
                             help=f"{selected_season_id} {filial} {group}"):
                    st.session_state.adding_child_filial_name = filial
                    st.session_state.adding_child_group_name = group
                    add_child_to_group()

        # Обновляем последний заполненный столбец
        last_filled_col = col_idx

    # Размещаем кнопку "Добавить группу" в следующей свободной колонке после всех групп
    next_col = (last_filled_col + 1) % num_cols
    with cols[next_col]:
        if st.button(":material/add_box:", key=f"add_group_to{filial}", help="Добавить группу в филиал"):
            season_selected_id = st.session_state.selected_season_id
            filial_id = sql_queries.get_filial_id_by_name_and_season(filial, season_selected_id)
            st.session_state.filial_id = filial_id
            add_group_to_filial()
    if st.button(":material/edit_square:", key=f"rename_filial_to{filial}", help=f"Переименовать филиал {filial}"):
        season_selected_id = st.session_state.selected_season_id
        st.session_state.rename_filial = sql_queries.get_filial_id_by_name_and_season(filial, season_selected_id)
        rename_filial()
    st.divider()
if st.button(":material/add_box:", key="add_fil", help="Добавить филиал"):
    add_filial()


def calculate_age(birth_date_str):
    date_format = "%d.%m.%Y"
    birth_date = datetime.strptime(birth_date_str, date_format)
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age
