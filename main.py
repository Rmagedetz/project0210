import streamlit as st
import sql
import docxtpl

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    with st.form("login_form", clear_on_submit=True):
        st.title("Вход в приложение")
        user_input = st.text_input("Введите логин")
        password_input = st.text_input("Введите пароль", type="password")
        submit = st.form_submit_button("Войти")

        if submit:
            if user_input in sql.get_user_list():
                if password_input == sql.check_user_password(user_input):
                    st.session_state.logged_in = True
                    st.session_state.user = user_input
                    st.session_state.role = sql.get_user_role(user_input)
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
            else:
                st.error("Неверный логин или пароль")


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Выйти", icon=":material/logout:")

users = st.Page("pages/settings/users.py", title="Пользователи", icon=":material/group:")
roles = st.Page("pages/settings/roles.py", title="Роли", icon=":material/manage_accounts:")

seasons = st.Page("pages/seasons_filials_groups/seasons.py", title="Сезоны")
filials = st.Page("pages/seasons_filials_groups/filials.py", title="Филиалы")
groups = st.Page("pages/seasons_filials_groups/groups.py", title="Группы")

leavers = st.Page("pages/childrens_info/leavers.py", title="Жители Городка")
gt_quiz = st.Page("pages/childrens_info/gt_quiz.py", title="Анкеты")
old_base = st.Page("pages/childrens_info/old_base.py", title="Старая база")

group_cards = st.Page("pages/group_cards/group_card.py", title="Карточки групп")

payments = st.Page('pages/payments and expenses/payments.py', title="Платежи")

records_v1 = st.Page("pages/records_variants/var_1.py", title="Записи (в1)",default=True)

bills = st.Page("pages/payments and expenses/bills.py", title="Списания")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Логин": [logout_page],
            "Пользователи и роли": [roles, users],
            "Администрирование": [seasons, filials, groups],
            "Данные детей": [leavers, gt_quiz, old_base],
            "Карточки групп": [group_cards],
            "Платежи и списания": [payments, bills],
            "Записи": [records_v1]
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
