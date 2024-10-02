import streamlit as st
import sql_queries

selected_season = st.session_state.get('selected_season', 'Сезон не выбран')

with st.sidebar:
    with st.container(border=True):
        fil_list = sql_queries.Filial.get_filial_list_for_season(selected_season)
        filial_selector = st.selectbox("Выберите филиал", fil_list, key="filial_selector")

        gr_list = sql_queries.Group.get_groups_list_for_season_and_filial(selected_season, filial_selector)
        group_selector = st.selectbox("Выберите группу", gr_list, key="group_selector")

g_card = sql_queries.Children.show_group_card(selected_season, filial_selector, group_selector)


def transform(df):
    try:
        return df[["child_name", "child_age", "child_parent_name", "child_parent_phone_num"]]
    except:
        return None


g_card = transform(g_card)
list_from_records, main_list, checkins, infolist, trip, lockers, pool = st.tabs(["Из записей",
                                                                                 "Список",
                                                                                 "Посещаемость",
                                                                                 "Лист ознакомления",
                                                                                 "Поездка",
                                                                                 "Список на шкафчики",
                                                                                 "Бассейн"])

with list_from_records:
    g_card = st.data_editor(g_card,
                            column_config={
                                "child_name": "Ф.И.О. Ребенка",
                                "child_age": "Возраст",
                                "child_parent_name": "Ф.И.О. Родителя",
                                "child_parent_phone_num": "Номер телефона"
                            })
