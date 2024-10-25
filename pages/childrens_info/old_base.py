import streamlit as st
import pandas as pd
from cryptography.fernet import Fernet
from pages.childrens_info.gt_quiz import save_encrypted_csv_from_dataframe, load_decrypted_csv_to_dataframe
import sql

crypt = st.secrets["crypt_key"]["key"]
cipher_suite = Fernet(crypt)

user_logged = st.session_state.user

st.write("Данные из старой базы")

decrypted_df = load_decrypted_csv_to_dataframe("old_base/encrypted_output.csv")
st.write(decrypted_df)


uploaded_file = st.file_uploader("Загрузите файл Excel", type="xlsx",
                                 disabled=not(sql.check_user_rights(user_logged, "editing_leavers")))

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
