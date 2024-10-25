import streamlit as st
import sql

user_logged = st.session_state.user

data = sql.get_users_dataframe()

st.data_editor(data,
               column_config={
                   "User Name": st.column_config.Column("Имя пользователя"),
                   "Role Name": st.column_config.Column("Роль")
               },
               hide_index=True)


@st.dialog("Добавление пользователя")
def add_user():
    username = st.text_input("Логин пользователя")
    existing_users_roles = sql.get_role_names()
    user_role = st.selectbox("Роль пользователя", existing_users_roles)
    user_pass = st.text_input("Пароль для пользователя", type="password")
    user_pass_confirmation = st.text_input("Подтверждение пароля", type="password")
    if st.button("Добавить пользователя", key="add_user_accept_btn"):
        if username in sql.get_user_list():
            st.error("Пользователь с таким именем уже существует")
        elif user_role is None:
            st.error("Выберите роль пользователя")
        elif user_pass != user_pass_confirmation:
            st.error("Пароли не совпадают")
        else:
            sql.add_user(username, user_pass, user_role)
            st.toast("Пользователь добавлен")
            st.rerun()


@st.dialog("Удаление пользователя")
def delete_user():
    user_list = sql.get_user_list()
    user_list.remove("superadmin")
    username = st.selectbox("Пользователь", user_list, index=None)
    if st.button("Удалить пользователя", key="user_deletion_accept_btn"):
        sql.delete_user_record(username)
        st.toast("Пользователь удален")
        st.rerun()


@st.dialog("Изменение пароля")
def update_userpass():
    user_list = sql.get_user_list()
    user_list.remove("superadmin")
    username = st.selectbox("Пользователь", user_list, index=None)
    new_pass = st.text_input("Новый пароль", type="password")
    pass_confirmation = st.text_input("Подтверждение пароля", type="password")
    if st.button("Изменить пароль для пользователя", key="userpass_change_accept_btn"):
        old_pass = sql.check_user_password(username)
        if new_pass == old_pass:
            st.error("Новый пароль совпадает со старым")
        elif new_pass != pass_confirmation:
            st.error("Пароли не совпадают")
        else:
            sql.update_user_password(username, new_data={"password": new_pass})
            st.toast("Пароль для пользователя обновлен")
            st.rerun()


@st.dialog("Изменить роль пользователя")
def update_user_role():
    user_list = sql.get_user_list()
    user_list.remove("superadmin")
    username = st.selectbox("Пользователь", user_list, index=None)
    existing_users_roles = sql.get_role_names()
    new_role = st.selectbox("Роль пользователя", existing_users_roles, index=None)
    if st.button("Изменить роль для пользователя", key="user_role_change_accept_btn"):
        sql.update_user_role(username, new_role)
        st.toast("Роль пользователя обновлена")
        st.rerun()


col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        if st.button("Добавить пользователя",
                     key="add_closing_doc_open_dialog_btn",
                     disabled=not (sql.check_user_rights(user_logged, "creating_users")),
                     use_container_width=True):
            add_user()

        if st.button("Удалить пользователя",
                     key="delete_user_open_dialog_btn",
                     disabled=not (sql.check_user_rights(user_logged, "deleting_users")),
                     use_container_width=True):
            delete_user()

        if st.button("Изменить пароль для пользователя",
                     key="update_userpass_open_dialog_btn",
                     disabled=not (sql.check_user_rights(user_logged, "editing_users")),
                     use_container_width=True):
            update_userpass()

        if st.button("Изменить роль для пользователя",
                     key="update_user_role_open_dialog",
                     disabled=not (sql.check_user_rights(user_logged, "editing_users")),
                     use_container_width=True):
            update_user_role()
