import streamlit as st
import pandas as pd
from cryptography.fernet import Fernet
from pages.childrens_info.gt_quiz import save_encrypted_csv_from_dataframe, load_decrypted_csv_to_dataframe
import sql
from docxtpl import DocxTemplate
import datetime

crypt = st.secrets["crypt_key"]["key"]
cipher_suite = Fernet(crypt)

user_logged = st.session_state.user

st.write("Данные из старой базы")


@st.dialog("Договор")
def make_order():
    data = decrypted_df
    child_list = decrypted_df["ФИО"].to_list()

    ord_num = st.text_input("Номер договора")
    checkbox = st.checkbox("Не из списка")

    if checkbox:
        child_fio_selector = st.text_input("ФИО ребенка:")
        adult_fio = st.text_input("ФИО родителя")
        child_birthday = st.date_input("ДР Ребенка", value=None)
        adult_passport = st.text_input("Паспортные данные родителя")
        adult_adress = st.text_input("Адрес регистрации родителя")
        child_adress = st.text_input("Адрес проживания ребенка")
        adult_phonenum = st.text_input("Номер телефона родителя")
        adult_email = st.text_input("Email")
    else:
        child_fio_selector = st.selectbox("ФИО Ребенка", child_list, index=None)
        if child_fio_selector:
            child_data = data[data["ФИО"] == child_fio_selector].reset_index(drop=True)
            adult_fio = st.text_input("ФИО родителя", value=child_data["Родитель (имя, телефон)"][0])
            child_birthday = st.date_input("ДР Ребенка", value=None)
            adult_passport = st.text_input("Паспортные данные родителя", value=child_data["Паспорт"][0])
            adult_adress = st.text_input("Адрес регистрации родителя", value=child_data["Адрес регистрации"][0])
            child_adress = st.text_input("Адрес проживания ребенка")
            adult_phonenum = st.text_input("Номер телефона родителя")
            adult_email = st.text_input("Email")

    if st.button("Сгенерировать договор"):
        if not ord_num:
            st.error("Введите номер договора")
        elif not child_fio_selector:
            st.error("Введите ФИО ребенка")
        elif not adult_fio:
            st.error("Введите ФИО взрослого")
        elif not child_birthday:
            st.error("Введите ДР ребенка")
        elif not adult_passport:
            st.error("Введите паспортные данные")
        elif not adult_adress:
            st.error("Введите адрес регистрации")
        elif not child_adress:
            st.error("Введите адрес проживания ребенка")
        elif not adult_phonenum:
            st.error("Введите номер телефона")
        elif not adult_email:
            st.error("Введите email")
        else:
            day = datetime.date.today().day
            month = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
                     7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}[
                datetime.date.today().month]
            year = datetime.date.today().year
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


decrypted_df = load_decrypted_csv_to_dataframe("old_base/encrypted_output.csv")
st.write(decrypted_df)

if st.button("Договор"):
    make_order()

uploaded_file = st.file_uploader("Загрузите файл Excel", type="xlsx",
                                 disabled=not (sql.check_user_rights(user_logged, "editing_leavers")))

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("Содержимое файла:")
    df = df[["ФИО", "Родитель (имя, телефон)", "Паспорт", "Адрес регистрации"]]
    st.dataframe(df)
    if st.button("Сохранить данные", key="save_data"):
        save_encrypted_csv_from_dataframe(df, "old_base/encrypted_output.csv")
        st.rerun()
else:
    st.info("Пожалуйста, загрузите файл .xlsx, чтобы увидеть содержимое.")
