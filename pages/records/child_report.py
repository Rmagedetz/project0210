import streamlit as st

import sql_queries

selected_season = st.session_state.get('selected_season', 'Сезон не выбран')
child_list = sql_queries.get_info_list()
child_fio_selector = st.selectbox("Ф.И.О Ребенка:", child_list, index=None)
df = sql_queries.get_info_dataframe()
df = df[df["child_name"] == child_fio_selector].reset_index()
base, payments = st.tabs(["Анкетные данные", "Платежи"])
with base:
    with st.container(border=True):
        st.write("Основные данные")
        main = df[["child_birthday", "parent_main", "phone_main", "parent_add", "phone_add", "leave",
                   "additional_contact",
                   "addr", "oms"]]
        main = main.rename(columns={"child_birthday": "Дата рождения ребенка",
                                    "parent_main": "ФИО родителя (законного представителя) для основной связи",
                                    "phone_main": "Телефон для основной связи",
                                    "parent_add": "ФИО другого взрослого",
                                    "phone_add": "Телефон для запасной связи",
                                    "leave": "Ребенок будет уходить сам по окончании дня?",
                                    "additional_contact": "Кто кроме родителя (законного представителя) может забирать "
                                                          "ребенка? ФИО, кем приходится, контактный телефон.",
                                    "addr": "Адрес фактического проживания ребенка",
                                    "oms": "Номер страхового медицинского полиса"})

        main = main.transpose()
        main = main.rename(columns={"": "", 0: ""})
        main = st.table(main)
    with st.container(border=True):
        st.write("Данные о состоянии здоровья")
        health = df[["disease", "allergy", "other", "physic"]]
        health = health.rename(columns={"disease": "Есть ли у ребенка заболевания (сердца, пищеварительной системы, "
                                                   "нервной системы, психические расстройства, опорно-двигательной "
                                                   "системы, внутренних органов). Если есть, поясните подробнее.",
                                        "allergy": "Есть ли у ребенка аллергическая реакция (если есть, укажите, "
                                                   "на что и как она проявляется): ",
                                        "other": "Были ли у ребенка (Операции, Переломы, Сотрясение мозга, Приступы "
                                                 "эпилепсии). Если да, поясните подробнее.",
                                        "physic": "Есть ли у ребенка ограничения по физическим нагрузкам? Если да, "
                                                  "поясните подробнее."})
        health = health.transpose()
        health = health.rename(columns={"": "", 0: ""})
        health = st.table(health)
    with st.container(border=True):
        st.write("Доплнительные сведения")
        additional = df[["swimm", "jacket_swimm", "hobby", "school", "additional_info"]]
        additional = additional.rename(columns={"swimm":"Будет ли ребенок посещать бассейн во время смены?",
                                                "jacket_swimm":"Нужны ли ребенку в бассейне нарукавники или жилет?",
                                                "hobby":"Нужны ли ребенку в бассейне нарукавники или жилет?",
                                                "school":"Какое учебное заведение посещает ребенок?",
                                                "additional_info":"Если вы хотите еще что-то рассказать нам о своем "
                                                                  "ребенке, напишите это здесь"})
        additional = additional.transpose()
        additional = additional.rename(columns={"": "", 0: ""})
        additional = st.table(additional)
with payments:
    table = sql_queries.get_payments_for_single_child(child_fio_selector)
    st.write(table)