import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import datetime
import sql_queries

import_file = st.sidebar.file_uploader("Добавить данные в базу")
if import_file is not None:
    database = pd.read_excel(import_file)
    data = database[["ФИО", "Телефон", "Email", "Дата рождения", "Родитель (имя, телефон)", "Паспорт",
                     "Адрес регистрации", "Адрес"]]
    data["Дата рождения"] = pd.to_datetime(data["Дата рождения"])
    data = data.fillna("-")
    st.write(data)

    if st.button("Добавить все в базу"):
        queries = []
        for index, row in data.iterrows():
            birthday = None if row["Дата рождения"] == "-" else row["Дата рождения"]
            query = sql_queries.persons(child_name=row["ФИО"],
                                        parent_phone_num=row["Телефон"],
                                        parent_email=row["Email"],
                                        child_birthday=birthday,
                                        parent_main=row["Родитель (имя, телефон)"],
                                        parent_passport=row["Паспорт"],
                                        parent_adress=row["Адрес регистрации"],
                                        child_adress=row["Адрес"])
            queries.append(query)
        st.write("Пакет данных сформирован")
        sql_queries.initiate_batch_query(queries, "Ошибка добавления в базу", batch_size=100)


@st.dialog("Генерация договора")
def generate_order():
    child_list = sql_queries.persons.get_list()

    ord_num = st.text_input("Номер договора:")
    day = datetime.date.today().day

    month = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
             7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}[
        datetime.date.today().month]
    year = datetime.date.today().year

    if st.checkbox("Не из списка"):
        child_fio_selector = st.text_input("ФИО ребенка:")
        adult_fio = ""
        child_birthday = ""
        adult_passport = ""
        adult_adress = ""
        child_adress = ""
        adult_phonenum = ""
        adult_email = ""
    else:
        child_fio_selector = st.selectbox("ФИО Ребенка", child_list, index=None)
        child_data = sql_queries.persons.get_as_dataframe_for_single_child(child_fio_selector)

        adult_fio = child_data.get("parent_main", [""])[0]
        child_birthday = child_data.get("child_birthday", [""])[0]
        adult_passport = child_data.get("parent_passport", [""])[0]
        adult_adress = child_data.get("parent_adress", [""])[0]
        child_adress = child_data.get("child_adress", [""])[0]
        adult_phonenum = child_data.get("parent_phone_num", [""])[0]
        adult_email = child_data.get("parent_email", [""])[0]

    with st.container(border=True):
        adult_fio = st.text_input("ФИО родителя:", adult_fio)
        adult_phonenum = st.text_input("Номер телефона:", adult_phonenum)
        adult_email = st.text_input("E-mail:", adult_email)
        child_adress = st.text_input("Адрес проживания ребенка:", child_adress)
        try:
            child_birthday = st.date_input("Дата рождения ребенка", child_birthday)
        except:
            child_birthday = st.date_input("Дата рождения ребенка")
        adult_passport = st.text_area("Паспортные данные родителя", adult_passport)
        adult_adress = st.text_input("Адрес прописки родителя", adult_adress)

    if st.button("Сгенерировать договор", key="generate_order_btn"):
        if ord_num != "":
            child_birth_year = child_birthday.year
            adult = adult_fio.split(" ")
            adult_initials = f"{adult[0]} {adult[1][0]}. {adult[2][0]}."
            doc = DocxTemplate("Order_mockup.docx")
            context = {'ord_num': ord_num, "day": day, "month": month, "year": year,
                       "adult_fio": adult_fio, "child_fio": child_fio_selector, "child_birth_year": child_birth_year,
                       "adult_passport": adult_passport, "adult_adress": adult_adress, "child_adress": child_adress,
                       "adult_phonenum": adult_phonenum, "adult_email": adult_email, "adult_initials": adult_initials}
            doc.render(context)
            doc.save("шаблон-final.docx")
            st.success("Договор сгенерирован")
            with open("шаблон-final.docx", "rb") as f:
                st.download_button('Скачать договор', f, file_name=f"Договор_{ord_num}.docx")
        else:
            st.error("Введите номер договора")


if st.button("Сгенерировать договор"):
    generate_order()
