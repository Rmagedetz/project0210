import streamlit as st
import google_sheet_connection
import pandas as pd
from cryptography.fernet import Fernet
import io
from datetime import datetime

import sql

user_logged = st.session_state.user

crypt = st.secrets["crypt_key"]["key"]
cipher_suite = Fernet(crypt)

update_file_path = "google_quiz_data/last_update.txt"


@st.dialog("Привязать анкету")
def set_quiz_data_to_child():
    data = decrypted_df.to_dict("index")
    quiz_id = st.number_input("ID анкеты", min_value=1, step=1, max_value=len(data))
    selected_quiz = data[quiz_id]
    selected_quiz = {key: (value if not pd.isna(value) else None) for key, value in selected_quiz.items()}

    with st.container(border=True):
        st.write(f"Ребенок: {selected_quiz["name"]}")
        st.write(f"Родитель: {selected_quiz["parent_main_name"]}")
        st.write(f"Email: {selected_quiz["email"]}")

    child_list = sql.get_children_list()
    child_selector = st.selectbox("Житель городка", child_list, index=None)

    if st.button("Привязать анкету", key="apply_quiz_to_child"):
        sql.update_child_quiz(child_selector, new_data=selected_quiz)
        st.rerun()


def save_encrypted_csv_from_dataframe(dataframe, file_path):
    csv_data = dataframe.to_csv(index=False).encode('utf-8')
    encrypted_data = cipher_suite.encrypt(csv_data)
    with open(file_path, 'wb') as file:
        file.write(encrypted_data)


def load_decrypted_csv_to_dataframe(file_path):
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    decrypted_csv = io.StringIO(decrypted_data.decode('utf-8'))
    dataframe = pd.read_csv(decrypted_csv)
    dataframe.index += 1
    return dataframe


def get_last_update():
    try:
        with open(update_file_path, 'r') as file:
            last_upd = file.read().strip()
    except FileNotFoundError:
        last_upd = "Нет данных о последнем обновлении."
    return last_upd


def update_last_update():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(update_file_path, 'w') as file:
        file.write(current_time)


last_update = get_last_update()
st.write(f"Данные анкет из гугла. Обновлено: {last_update}")
decrypted_df = load_decrypted_csv_to_dataframe("google_quiz_data/encrypted_output.csv")
st.write(decrypted_df)

if st.button("Обновить данные", disabled=not(sql.check_user_rights(user_logged, "editing_leavers"))):
    st.toast("Подключаемся к гугл-таблице")
    new_data = google_sheet_connection.get_quiz_data()
    st.toast("Обрабатываем данные")
    save_encrypted_csv_from_dataframe(new_data, "google_quiz_data/encrypted_output.csv")
    update_last_update()
    st.rerun()
if st.button("Привязать анкету",disabled=not(sql.check_user_rights(user_logged, "editing_leavers"))):
    set_quiz_data_to_child()
