import streamlit as st
import sql_queries

selected_season = st.session_state.season_selected
season_id = sql_queries.get_season_id_by_name(selected_season)
filials_list = sql_queries.get_filials_list_for_season(season_id)
col1, col2 = st.columns(2)
with col1:
    filial_selected = st.selectbox("Филиал", filials_list)
with col2:
    filial_id = sql_queries.get_filial_id_by_name_and_season(filial_selected, season_id)
    groups_list = sql_queries.get_groups_list_for_season_and_filial(season_id, filial_id)
    group_selected = st.selectbox("Группа", groups_list)
    group_id = sql_queries.get_group_id(season_id, filial_id, group_selected)


def transform(df):
    try:
        return df[["child_name", "child_age", "child_parent_name", "child_parent_num"]]
    except:
        return None


g_card = sql_queries.show_group_card(season_id=season_id, filial_id=filial_id, group_id=group_id)

list_from_records, main_list, checkins, infolist, trip, lockers, pool = st.tabs(["Из записей",
                                                                                 "Список",
                                                                                 "Посещаемость",
                                                                                 "Лист ознакомления",
                                                                                 "Поездка",
                                                                                 "Список на шкафчики",
                                                                                 "Бассейн"])

with list_from_records:
    g_card = transform(g_card)
    if g_card is not None:
        g_card.index = g_card.index + 1

    g_card = st.data_editor(g_card,
                            column_config={
                                "child_name": "Ф.И.О. Ребенка",
                                "child_age": "Возраст",
                                "child_parent_name": "Ф.И.О. Родителя",
                                "child_parent_num": "Номер телефона"
                            })
