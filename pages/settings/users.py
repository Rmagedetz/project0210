import streamlit as st

import sql_queries

data = sql_queries.UsersTable.get_as_dataframe()

st.data_editor(data,
               column_config={
                   "user_name": st.column_config.Column("Имя пользователя"),
                   "user_role": st.column_config.Column("Роль")
               },
               hide_index=True)


@st.dialog("Добавление пользователя")
def add_user():
    username = st.text_input("Логин пользователя")
    existing_users_roles = [1, 2, 3, 4]
    user_role = st.selectbox("Роль пользователя", existing_users_roles)
    user_pass = st.text_input("Пароль для пользователя", type="password")
    user_pass_confirmation = st.text_input("Подтверждение пароля", type="password")
    if st.button("Добавить пользователя", key="add_user_accept_btn"):
        if username in sql_queries.UsersTable.get_list():
            st.error("Пользователь с таким именем уже существует")
        elif user_role is None:
            st.error("Выберите роль пользователя")
        elif user_pass != user_pass_confirmation:
            st.error("Пароли не совпадают")
        else:
            sql_queries.UsersTable.add_record(username, user_pass, user_role)
            st.toast("Пользователь добавлен")
            st.rerun()


@st.dialog("Удаление пользователя")
def delete_user():
    user_list = sql_queries.UsersTable.get_list()
    user_list.remove("superadmin")
    username = st.selectbox("Пользователь", user_list)
    if st.button("Удалить пользователя", key="user_deletion_accept_btn"):
        sql_queries.UsersTable.delete_record(username)
        st.toast("Пользователь удален")
        st.rerun()


@st.dialog("Изменение пароля")
def update_userpass():
    user_list = sql_queries.UsersTable.get_list()
    user_list.remove("superadmin")
    username = st.selectbox("Пользователь", user_list)
    new_pass = st.text_input("Новый пароль", type="password")
    pass_confirmation = st.text_input("Подтверждение пароля", type="password")
    if st.button("Изменить пароль для пользователя", key="userpass_change_accept_btn"):
        old_pass = sql_queries.UsersTable.check_pass(username)
        if new_pass == old_pass:
            st.error("Новый пароль совпадает со старым")
        elif new_pass != pass_confirmation:
            st.error("Пароли не совпадают")
        else:
            sql_queries.UsersTable.update_password(username, new_pass)
            st.toast("Пароль для пользователя обновлен")
            st.rerun()


@st.dialog("Изменить роль пользователя")
def update_user_role():
    user_list = sql_queries.UsersTable.get_list()
    user_list.remove("superadmin")
    username = st.selectbox("Пользователь", user_list)
    existing_users_roles = [1, 2, 3, 4]
    new_role = st.selectbox("Роль пользователя", existing_users_roles)
    if st.button("Изменить роль для пользователя", key="user_role_change_accept_btn"):
        sql_queries.UsersTable.update_role(username, new_role)
        st.toast("Роль пользователя обновлена")
        st.rerun()


if st.sidebar.button("Добавить пользователя",
                     key="add_closing_doc_open_dialog_btn", disabled=False):
    add_user()

if st.sidebar.button("Удалить пользователя",
                     key="delete_user_open_dialog_btn", disabled=False):
    delete_user()

if st.sidebar.button("Изменить пароль для пользователя",
                     key="update_userpass_open_dialog_btn", disabled=False):
    update_userpass()

if st.sidebar.button("Изменить роль для пользователя",
                     key="update_user_role_open_dialog", disabled=False):
    update_user_role()
