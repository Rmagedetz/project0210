import streamlit as st
import sql

user_logged = st.session_state.user

data = sql.get_roles_dataframe()
st.write(data)


@st.dialog("Создание роли")
def add_role():
    role_name = st.text_input("Название роли")
    with st.container(border=True):
        st.subheader("Роли")
        creating_roles = st.checkbox("Создание", key=1)
        editing_roles = st.checkbox("Редактирование", key=2)
        deleting_roles = st.checkbox("Удаление", key=3)
    with st.container(border=True):
        st.subheader("Пользователи")
        creating_users = st.checkbox("Создание", key=4)
        editing_users = st.checkbox("Редактирование", key=5)
        deleting_users = st.checkbox("Удаление", key=6)
    with st.container(border=True):
        st.subheader("Сезоны")
        adding_seasons = st.checkbox("Создание", key=7)
        editing_seasons = st.checkbox("Редактирование", key=8)
        deleting_seasons = st.checkbox("Удаление", key=9)
    with st.container(border=True):
        st.subheader("Филиалы")
        adding_filials = st.checkbox("Создание", key=10)
        editing_filials = st.checkbox("Редактирование", key=11)
        deleting_filials = st.checkbox("Удаление", key=12)
    with st.container(border=True):
        st.subheader("Группы")
        adding_groups = st.checkbox("Создание", key=13)
        editing_groups = st.checkbox("Редактирование", key=14)
        deleting_groups = st.checkbox("Удаление", key=15)
    with st.container(border=True):
        st.subheader("Жители")
        adding_leavers = st.checkbox("Создание", key=16)
        editing_leavers = st.checkbox("Редактирование", key=17)
        deleting_leavers = st.checkbox("Удаление", key=18)
    with st.container(border=True):
        st.subheader("Платежи")
        adding_payments = st.checkbox("Создание", key=19)
        editing_payments = st.checkbox("Редактирование", key=20)
        deleting_payments = st.checkbox("Удаление", key=21)
    with st.container(border=True):
        st.subheader("Списания")
        adding_cancelations = st.checkbox("Создание", key=22)
        editing_cancelations = st.checkbox("Редактирование", key=23)
        deleting_cancelations = st.checkbox("Удаление", key=24)
    if st.button("Создать роль", key="role_create_confirmation"):
        if not role_name:
            st.error("Ведите название роли")
        else:
            existing = sql.get_role_names()
            if role_name in existing:
                st.error("Роль с таким именем уже существует")
            else:
                sql.add_role(role_name=role_name,
                             creating_roles=creating_roles,
                             editing_roles=editing_roles,
                             deleting_roles=deleting_roles,
                             creating_users=creating_users,
                             editing_users=editing_users,
                             deleting_users=deleting_users,
                             adding_seasons=adding_seasons,
                             editing_seasons=editing_seasons,
                             deleting_seasons=deleting_seasons,
                             adding_filials=adding_filials,
                             editing_filials=editing_filials,
                             deleting_filials=deleting_filials,
                             adding_groups=adding_groups,
                             editing_groups=editing_groups,
                             deleting_groups=deleting_groups,
                             adding_leavers=adding_leavers,
                             editing_leavers=editing_leavers,
                             deleting_leavers=deleting_leavers,
                             adding_payments=adding_payments,
                             editing_payments=editing_payments,
                             deleting_payments=deleting_payments,
                             adding_cancelations=adding_cancelations,
                             editing_cancelations=editing_cancelations,
                             deleting_cancelations=deleting_cancelations
                             )
                st.rerun()


@st.dialog("Удаление роли")
def delete_role():
    role_selector = st.selectbox("Выберите роль", sql.get_role_names(), index=None)
    if st.button("Удалить роль", key="delete_role_accept"):
        sql.delete_role(role_selector)
        st.rerun()


@st.dialog("Редактирование роли")
def edit_role():
    roles = sql.get_roles_dataframe()
    select_role = st.selectbox("Выберите роль:", sql.get_role_names(), index=None)
    info = roles[roles["role_name"] == select_role].reset_index()
    if select_role:
        new_name = st.text_input("Ноаое название роли", select_role)
        with st.container(border=True):
            st.subheader("Роли")
            creating_roles = st.checkbox("Создание", key=1, value=info["creating_roles"][0])
            editing_roles = st.checkbox("Редактирование", key=2, value=info["editing_roles"][0])
            deleting_roles = st.checkbox("Удаление", key=3, value=info["deleting_roles"][0])
        with st.container(border=True):
            st.subheader("Пользователи")
            creating_users = st.checkbox("Создание", key=4, value=info["creating_users"][0])
            editing_users = st.checkbox("Редактирование", key=5, value=info["editing_users"][0])
            deleting_users = st.checkbox("Удаление", key=6, value=info["deleting_users"][0])
        with st.container(border=True):
            st.subheader("Сезоны")
            adding_seasons = st.checkbox("Создание", key=7, value=info["adding_seasons"][0])
            editing_seasons = st.checkbox("Редактирование", key=8, value=info["editing_seasons"][0])
            deleting_seasons = st.checkbox("Удаление", key=9, value=info["deleting_seasons"][0])
        with st.container(border=True):
            st.subheader("Филиалы")
            adding_filials = st.checkbox("Создание", key=10, value=info["adding_filials"][0])
            editing_filials = st.checkbox("Редактирование", key=11, value=info["editing_filials"][0])
            deleting_filials = st.checkbox("Удаление", key=12, value=info["deleting_filials"][0])
        with st.container(border=True):
            st.subheader("Группы")
            adding_groups = st.checkbox("Создание", key=13, value=info["adding_groups"][0])
            editing_groups = st.checkbox("Редактирование", key=14, value=info["editing_groups"][0])
            deleting_groups = st.checkbox("Удаление", key=15, value=info["deleting_groups"][0])
        with st.container(border=True):
            st.subheader("Жители")
            adding_leavers = st.checkbox("Создание", key=16, value=info["adding_leavers"][0])
            editing_leavers = st.checkbox("Редактирование", key=17, value=info["editing_leavers"][0])
            deleting_leavers = st.checkbox("Удаление", key=18, value=info["deleting_leavers"][0])
        with st.container(border=True):
            st.subheader("Платежи")
            adding_payments = st.checkbox("Создание", key=19, value=info["adding_payments"][0])
            editing_payments = st.checkbox("Редактирование", key=20, value=info["editing_payments"][0])
            deleting_payments = st.checkbox("Удаление", key=21, value=info["deleting_payments"][0])
        with st.container(border=True):
            st.subheader("Списания")
            adding_cancelations = st.checkbox("Создание", key=22, value=info["adding_cancelations"][0])
            editing_cancelations = st.checkbox("Редактирование", key=23, value=info["editing_cancelations"][0])
            deleting_cancelations = st.checkbox("Удаление", key=24, value=info["deleting_cancelations"][0])

        if st.button("Редактировать роль"):
            sql.update_role(select_role,
                            new_data={"role_name": new_name,
                                      "creating_roles": creating_roles,
                                      "editing_roles": editing_roles,
                                      "deleting_roles": deleting_roles,
                                      "creating_users": creating_users,
                                      "editing_users": editing_users,
                                      "deleting_users": deleting_users,
                                      "adding_seasons": adding_seasons,
                                      "editing_seasons": editing_seasons,
                                      "deleting_seasons": deleting_seasons,
                                      "adding_filials": adding_filials,
                                      "editing_filials": editing_filials,
                                      "deleting_filials": deleting_filials,
                                      "adding_groups": adding_groups,
                                      "editing_groups": editing_groups,
                                      "deleting_groups": deleting_groups,
                                      "adding_leavers": adding_leavers,
                                      "editing_leavers": editing_leavers,
                                      "deleting_leavers": deleting_leavers,
                                      "adding_payments": adding_payments,
                                      "editing_payments": editing_payments,
                                      "deleting_payments": deleting_payments,
                                      "adding_cancelations": adding_cancelations,
                                      "editing_cancelations": editing_cancelations,
                                      "deleting_cancelations": deleting_cancelations
                                      })
            st.rerun()


col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        if st.button("Создать роль",
                     key="create_role",
                     disabled=not (sql.check_user_rights(user_logged, "creating_roles")),
                     use_container_width=True):
            add_role()

        if st.button("Удалить роль",
                     key="delete_role",
                     disabled=not (sql.check_user_rights(user_logged, "deleting_roles")),
                     use_container_width=True):
            delete_role()

        if st.button("Редактировать роль",
                     key="edit_role",
                     disabled=not (sql.check_user_rights(user_logged, "editing_roles")),
                     use_container_width=True):
            edit_role()
