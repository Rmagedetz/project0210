import streamlit as st
import sql

user_logged = st.session_state.user


@st.dialog("Добавление жителя")
def add_leaver():
    name = st.text_input("Имя ребенка")
    age = st.number_input("Возраст ребенка", step=1)
    parent_name = st.text_input("ФИО Родителя")
    parent_phone = st.text_input("Телефон родителя")
    if st.button("Добавить ребенка"):
        if name == "":
            st.error("Введите имя ребенка")
        elif age == 0:
            st.error("Введите возраст ребенка")
        elif parent_name == "":
            st.error("Введите ФИО родителя")
        elif parent_phone == "":
            st.error("Введите номер телефона родителя")
        else:
            child_data = {"name": name,
                          "age": age,
                          "parent_main_name": parent_name,
                          "parent_main_phone": parent_phone}
            success = sql.add_leaver(child_data)
            if success:
                st.rerun()
            else:
                st.error("Ребенок с таким именем уже существует")


@st.dialog("Редактирование данных ребенка")
def edit_leaver():
    child_list = sql.get_children_list()
    selector = st.selectbox("Ребенок", child_list, index=None)
    if selector:
        child_data = sql.get_all_child_data(selector)
        base_data, quiz_data, doc_data = st.tabs(["Основные данные", "Анкетные данные", "Паспортные данные"])
        with base_data:
            new_name = st.text_input("Имя ребенка", child_data["name"], key="new_name")
            new_age = st.number_input("Возраст ребенка", step=1, value=child_data["age"], key="new_age")
            new_parent_name = st.text_input("ФИО Родителя", value=child_data["parent_main_name"], key="new_parent")
            new_parent_phone = st.text_input("Телефон Родителя", value=child_data["parent_main_phone"], key="new_phone")
        with quiz_data:
            new_mail = st.text_input("Электронная почта", value=child_data["email"], key="new_mail")
            new_birthday = st.date_input("Дата рождения", value=child_data["child_birthday"], key="new_birthday")
            new_parent_add = st.text_input("Дополнительный контакт", value=child_data["parent_add"], key="new_p_a")
            new_phone_add = st.text_input("Дополнительный номер", value=child_data["phone_add"], key="new_p_p")
            new_leave = st.selectbox("Уходит сам?", ["да", "нет"], index=None, key="new_leave")
            new_additional_contact = st.text_input("Дополнительный контакт",
                                                   value=child_data["additional_contact"], key="new_a_c")
            new_addr = st.text_input("Адрес", value=child_data["addr"], key="new_adr")
            new_disease = st.text_input("Заболевания", value=child_data["disease"], key="new_disease")
            new_allergy = st.text_input("Аллергия", value=child_data["allergy"], key="new_aller")
            new_other = st.text_input("Операции", value=child_data["other"], key="new_oper")
            new_physic = st.text_input("Ограничения", value=child_data["physic"], key="new_phys")
            new_swimm = st.selectbox("Бассейн", ["да", "нет"], index=None, key="swimm")
            new_jacket_swimm = st.selectbox("Нарукавники", ["да", "нет"], index=None, key="jacket")
            new_hobby = st.text_input("Хобби", value=child_data["hobby"], key="hobby")
            new_school = st.text_input("Школа", value=child_data["school"], key="school")
            new_additional_info = st.text_input("Доп информация",
                                                value=child_data["additional_info"], key="add_info")
            new_departures = st.text_input("Прогулки", value=child_data["departures"], key="walks")
            new_referer = st.text_input("Откуда узнали", value=child_data["referer"], key="referer")
            new_ok = st.text_input("Подтверждение сведений", value=child_data["ok"], key="check")
            new_mailing = st.text_input("Согласие на рассылку", value=child_data["mailing"], key="mailing")
            new_personal_accept = st.text_input("Обработка персональных данных",
                                                value=child_data["personal_accept"], key="pd")
            new_oms = st.text_input("Номер ОМС", value=child_data["oms"], key="oms")

        with doc_data:
            new_parent_passport = st.text_input("Паспорт", value=child_data["parent_passport"], key="passp")
            new_parent_adress = st.text_input("Адрес", value=child_data["parent_adress"], key="addr")

        if st.button("Изменить данные", key="change_child_data_accept"):
            updated_data = {'name': new_name,
                            'age': new_age,
                            'parent_main_name': new_parent_name,
                            'parent_main_phone': new_parent_phone,
                            "email": new_mail,
                            "child_birthday": new_birthday,
                            "parent_add": new_parent_add,
                            "phone_add": new_phone_add,
                            "leave": new_leave,
                            "additional_contact": new_additional_contact,
                            "addr": new_addr,
                            "disease": new_disease,
                            "allergy": new_allergy,
                            "other": new_other,
                            "physic": new_physic,
                            "swimm": new_swimm,
                            "jacket_swimm": new_jacket_swimm,
                            "hobby": new_hobby,
                            "school": new_school,
                            "additional_info": new_additional_info,
                            "departures": new_departures,
                            "referer": new_referer,
                            "ok": new_ok,
                            "mailing": new_mailing,
                            "personal_accept": new_personal_accept,
                            "oms": new_oms,
                            "parent_passport": new_parent_passport,
                            "parent_adress": new_parent_adress}
            result = sql.update_child_quiz(selector, updated_data)
            if result:
                st.rerun()
            else:
                st.error("Ребенок с таким именем уже существует")


@st.dialog("Удаление жителя")
def delete_leaver():
    child_list = sql.get_children_list()
    selector = st.selectbox("Ребенок", child_list, index=None)
    if selector:
        if st.button("Удалить ребенка", key="delete_leaver_accept"):
            sql.delete_leaver(selector)
            st.rerun()


st.write("Жители Городка")


children = sql.get_children_dataframe()
st.write(children)

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        if st.button("Добавить жителя", key="add_leaver_btn",
                     disabled=not (sql.check_user_rights(user_logged, "adding_leavers")),
                     use_container_width=True):
            add_leaver()
        if st.button("Изменить данные жителя", key="change_leaver_data_btn",
                     disabled=not (sql.check_user_rights(user_logged, "editing_leavers")),
                     use_container_width=True):
            edit_leaver()
        if st.button("Удалить жителя", key="delete_leaver_data_bts",
                     disabled=not (sql.check_user_rights(user_logged, "deleting_leavers")),
                     use_container_width=True):
            delete_leaver()


# Вызов функции для отображения информации на странице Streamlit
# groups_info = sql.get_groups_with_children_count_and_paid_by_season(season_name="Сезон 11")
# st.write(groups_info)