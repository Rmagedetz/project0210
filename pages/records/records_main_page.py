import streamlit as st
import sql_queries
from datetime import datetime


def calculate_age(birth_date_str):
    date_format = "%d.%m.%Y"
    birth_date = datetime.strptime(birth_date_str, date_format)
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def show_groups_for_filial(groups_list, fil_name, divider):
    with st.container(border=True):
        st.subheader(fil_name, divider=divider)

        # Создание столбцов
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        num_cols = 5

        for i, group in enumerate(groups_list):
            col_idx = i % num_cols
            with cols[col_idx]:
                with st.container(border=True):
                    st.write(group)
                    show_group_info(fil_name, group)

                    # Передаем имя филиала в draw_buttons
                    draw_buttons(group, fil_name)

        st.divider()

        # Кнопки для добавления группы или удаления филиала
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            if st.button(":material/library_add:", key=f"add_group_to_{fil_name}", help="Добавить группу"):
                st.session_state['filial_name'] = fil_name  # Сохраняем филиал перед добавлением группы
                add_group()
        with subcol2:
            if st.button(":material/delete_forever:", key=f"delete_{fil_name}", help="Удалить филиал"):
                st.session_state['filial_name'] = fil_name  # Сохраняем филиал перед удалением
                delete_filial()


def draw_buttons(group_name, filial_name):
    col1, col2 = st.columns(2)

    # Кнопка для добавления ребенка в группу
    with col1:
        if st.button(":material/person_add:", key=f"add_child_to_{filial_name}_{group_name}",
                     help="Добавить ребенка в группу"):
            # Сохраняем выбранный филиал и группу в session_state
            st.session_state['selected_filial'] = filial_name
            st.session_state['selected_group'] = group_name
            add_to_group()


def show_group_info(fil_name, group_name):
    season = st.session_state.selected_season
    total = show_child_total_quantity_for_group(season, fil_name, group_name)
    recorded = show_child_recorded_quantity_for_group(season, fil_name, group_name)
    left = total - recorded
    st.write(f"Осталось: {left}\nБронь: {recorded}")


def show_child_total_quantity_for_group(season, fil_name, group_name):
    quantity = sql_queries.Group.request_children_quantity(season, fil_name, group_name)
    return quantity


def show_child_recorded_quantity_for_group(season, fil_name, group_name):
    try:
        quantity = sql_queries.Children.request_children_recorded(season, fil_name, group_name)
        return quantity
    except:
        return 0


@st.dialog("Удалить филиал")
def delete_filial():
    st.write("Внимание. Удаление филиала приведет к удалению всех групп в филиале")
    accept = st.checkbox("Я подтверждаю удаление филиала")
    if st.button("Удалить филиал"):
        if accept:
            sql_queries.Filial.delete_record(st.session_state.filial_name)
            st.rerun()
        else:
            st.error("Подтвердите удаление филиала")


@st.dialog("Добавление сезона")
def add_season():
    season_name = st.text_input("Название сезона")
    season_start_date = st.date_input("Дата начала сезона")
    season_end_date = st.date_input("Дата окончания сезона")
    if st.button("Добавить сезон"):
        if season_name in sql_queries.Season.get_list():
            st.error("Сезон с таким названием уже существует")
        else:
            sql_queries.Season.add_record(season_name=season_name,
                                          season_start=season_start_date,
                                          season_end=season_end_date)
            st.rerun()


@st.dialog("Добавление записи в группу")
def add_to_group():
    filial = st.session_state.get('selected_filial')
    group = st.session_state.get('selected_group')

    if not filial or not group:
        st.error("Филиал или группа не выбраны")
        return

    st.write(f"Филиал: {filial}, Группа: {group}")

    season = st.session_state.selected_season
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
            parent_list = list(set(sql_queries.Children.get_parent_list()))
            not_in_list = st.checkbox("Родителя нет в списке")
            if not_in_list:
                parent_input = st.text_input("Добавить родителя")
            else:
                parent_input = st.selectbox("ФИО родителя из списка", parent_list)

        if st.button("Добавить запись"):
            # Проверяем наличие актуальных данных
            if filial and group and child and age and parent_input:
                sql_queries.Children.add_record(
                    child_name=child,
                    child_age=age,
                    child_parent_name=parent_input,
                    child_parent_phone_num=phonenum,
                    child_season=season,
                    child_filial=filial,
                    child_group=group
                )
                st.success("Ребенок успешно добавлен в группу")
                st.rerun()
            else:
                st.error("Проверьте заполненные данные")
    else:
        # Логика для добавления из анкеты
        child_list = sql_queries.Info.get_list()
        child_selector = st.selectbox("Выберите ребенка", child_list)
        data = sql_queries.Info.get_data_for_group_addition(child_selector)
        birthday, parent, phonenum = data
        age = calculate_age(birthday)
        if st.button("Добавить запись"):
            sql_queries.Children.add_record(
                child_name=child_selector,
                child_age=age,
                child_parent_name=parent,
                child_parent_phone_num=phonenum,
                child_season=season,
                child_filial=filial,
                child_group=group
            )
            st.success("Ребенок успешно добавлен в группу")
            st.rerun()


@st.dialog("Добавление филиала")
def add_filial():
    fil_name = st.text_input("Название филиала")
    if st.button("Добавить филиал"):
        sql_queries.Filial.add_record(filial_name=fil_name,
                                      season=st.session_state.selected_season)
        st.rerun()


@st.dialog("Добавление группы в филиал")
def add_group():
    filial_name = st.session_state.get('filial_name')

    if not filial_name:
        st.error("Филиал не выбран")
        return

    group_name = st.text_input("Название группы")
    start_date = st.date_input("Дата начала")
    end_date = st.date_input("Дата окончания")
    children_count = st.number_input("Количество детей")

    if st.button("Добавить группу"):
        if group_name not in sql_queries.Group.get_list():
            sql_queries.Group.add_group(
                group_name=group_name,
                season=st.session_state.selected_season,
                filial=filial_name,
                start_date=start_date,
                end_date=end_date,
                children_count=children_count
            )
            st.success(f"Группа {group_name} добавлена в филиал {filial_name}")
            st.rerun()
        else:
            st.error("Группа с таким именем уже существует")


season_selector = st.sidebar.selectbox("Сезон", sql_queries.Season.get_list())
st.session_state['selected_season'] = season_selector

if st.sidebar.button(":material/add_box:", key="add_seas", help="Добавить сезон"):
    add_season()

filials = sql_queries.Filial.get_filial_list_for_season(season_selector)
groups = sql_queries.Group.get_as_dataframe()

for filial in filials:
    try:
        filtered_groups = groups[groups['filial'] == filial]["group_name"].tolist()
    except:
        filtered_groups = []
    show_groups_for_filial(filtered_groups, filial, "green")

if st.button(":material/add_box:", key="add_fil", help="Добавить филиал"):
    add_filial()
