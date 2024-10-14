import streamlit as st
import sql_queries
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
            if user_input in sql_queries.UsersTable.get_list():
                if password_input == sql_queries.UsersTable.check_pass(user_input):
                    st.session_state.logged_in = True
                    st.session_state.user = user_input
                    st.session_state.role = sql_queries.UsersTable.get_role(user_input)
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
records_main = st.Page("pages/records/records_main_page.py", title="Записи", icon=":material/menu_book:", default=True)
group_cards = st.Page("pages/records/group_cards.py", title="Карточки смен", icon=":material/groups:")
payments = st.Page("pages/records/payments_page.py", title="Оплаты", icon=":material/payments:")
debts = st.Page("pages/records/debts.py", title="Списания", icon=":material/check:")
child_report = st.Page("pages/records/child_report.py", title="Отчет по ребенку", icon=":material/child_care:")
parent_report = st.Page("pages/records/parent_report.py", title="Отчет по родителю",
                        icon=":material/escalator_warning:")
ord_gen_page = st.Page("pages/documents/ord_gen.py", title="Сгенерировать договор", icon=":material/history_edu:")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Логин": [logout_page],
            "Пользователи и роли": [users, roles],
            "Записи": [records_main, group_cards, payments, debts, child_report, parent_report],
            "Документы": [ord_gen_page]
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
