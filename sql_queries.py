from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from connections import sql_connection_string
import datetime
import pandas as pd
import time
import streamlit as st

Base = declarative_base()


def get_table_as_dataframe(cls, on_error_text, columns_order=None, column=None, column_value=None):
    session = Session()

    try:
        if column is None:
            query = session.query(cls).all()
        else:
            query = session.query(cls).filter(column == column_value).all()
        dataframe = pd.DataFrame([item.__dict__ for item in query])
        dataframe.drop(columns='_sa_instance_state', inplace=True)

        if columns_order:
            missing_cols = [col for col in columns_order if col not in dataframe.columns]
            if missing_cols:
                raise ValueError(f"Столбцы {missing_cols} отсутствуют в таблице.")
            dataframe = dataframe.reindex(columns=columns_order)
        return dataframe

    except Exception as e:
        print(f"{on_error_text} : {e}")
        return pd.DataFrame()

    finally:
        session.close()


def get_list(cls, column_name, on_error_text):
    session = Session()

    try:
        column = getattr(cls, column_name, None)
        if column is None:
            raise ValueError(f"Столбец {column_name} не существует.")
        results = session.query(cls).with_entities(column).all()
        return [result[0] for result in results]

    except Exception as e:
        print(f"{on_error_text} : {e}")
        return []

    finally:
        session.close()


def initiate_batch_query(queries, on_error_text, batch_size=100):
    """
    Выполняет пакетную вставку записей в базу данных с отслеживанием прогресса.

    :param queries: Список объектов, которые нужно вставить в базу данных.
    :param on_error_text: Текст ошибки, который выводится в случае неудачи.
    :param batch_size: Размер партии для вставки (по умолчанию 100 записей за раз).
    """
    session = Session()

    total_records = len(queries)
    st.write(f"Начало пакетной вставки {total_records} записей...")
    st.success(f"Начало пакетной вставки {total_records} записей...")

    try:
        start_time = time.time()

        # Проходим по списку записей с шагом batch_size
        for i in range(0, total_records, batch_size):
            batch = queries[i:i + batch_size]
            session.add_all(batch)
            session.commit()

            # Отслеживание прогресса
            print(f"Вставлено {min(i + batch_size, total_records)} из {total_records} записей.")
            st.success(f"Вставлено {min(i + batch_size, total_records)} из {total_records} записей.")

        elapsed_time = time.time() - start_time
        print(f"Все записи добавлены успешно за {elapsed_time:.2f} секунд!")
        st.success(f"Все записи добавлены успешно за {elapsed_time:.2f} секунд!")

    except Exception as e:
        session.rollback()
        print(f"{on_error_text} : {e}")
    finally:
        session.close()
        print("Сессия закрыта.")


class persons(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    child_name = Column(String(300))
    parent_phone_num = Column(String(300))
    parent_email = Column(String(300))
    child_birthday = Column(DateTime())
    parent_main = Column(String(300))
    parent_passport = Column(String(300))
    parent_adress = Column(String(300))
    child_adress = Column(String(300))


def get_persons_list():
    return get_list(persons, 'child_name', "Ошибка при загрузке списка детей")


class UsersTable(Base):
    __tablename__ = "Users_new"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(300), nullable=False)
    user_password = Column(String(100), nullable=False)

    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role = relationship("Role", back_populates="users")


class Role(Base):
    __tablename__ = 'roles'

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(300), unique=True, nullable=False)

    users = relationship("User", back_populates="role", cascade="all, delete")


class Info(Base):
    __tablename__ = "info"
    info_id = Column(Integer, primary_key=True)
    email = Column(String(300))
    child_name = Column(String(300))
    child_birthday = Column(String(300))
    parent_main = Column(String(300))
    phone_main = Column(String(300))
    parent_add = Column(String(300))
    phone_add = Column(String(300))
    leave = Column(String(300))
    additional_contact = Column(String(300))
    addr = Column(String(300))
    disease = Column(String(300))
    allergy = Column(String(300))
    other = Column(String(300))
    physic = Column(String(300))
    swimm = Column(String(300))
    jacket_swimm = Column(String(300))
    hobby = Column(String(300))
    school = Column(String(300))
    additional_info = Column(String(300))
    departures = Column(String(300))
    referer = Column(String(300))
    ok = Column(String(300))
    mailing = Column(String(300))
    personal_accept = Column(String(300))
    oms = Column(String(300))


class Season(Base):
    __tablename__ = 'seasons'

    season_id = Column(Integer, primary_key=True)
    season_name = Column(String(100), nullable=False)
    season_start_date = Column(Date, nullable=False)
    season_end_date = Column(Date, nullable=False)
    filials = relationship('Filial', back_populates='season', cascade="all, delete-orphan")


class Filial(Base):
    __tablename__ = 'filials'

    filial_id = Column(Integer, primary_key=True)
    filial_name = Column(String(100), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.season_id'))
    season = relationship('Season', back_populates='filials')
    groups = relationship('Group', back_populates='filial', cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = 'groups'

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(100), nullable=False)
    group_size = Column(Integer, nullable=False)
    group_start_date = Column(Date, nullable=False)
    group_end_date = Column(Date, nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.season_id'))
    filial_id = Column(Integer, ForeignKey('filials.filial_id'))
    filial = relationship('Filial', back_populates='groups')
    children_recorded = Column(Integer, nullable=False)
    children_payed = Column(Integer, nullable=False)
    children = relationship('Child', back_populates='group', cascade="all, delete-orphan")


class Child(Base):
    __tablename__ = 'children'

    child_id = Column(Integer, primary_key=True)
    child_name = Column(String(100), nullable=False)
    child_age = Column(Integer, nullable=False)
    child_parent_name = Column(String(100), nullable=False)
    child_parent_num = Column(String(20), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.season_id'))
    filial_id = Column(Integer, ForeignKey('filials.filial_id'))
    group_id = Column(Integer, ForeignKey('groups.group_id'))
    group = relationship('Group', back_populates='children')


class Payments(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True)
    worker_login = Column(String(300))
    payment_creation_time = Column(DateTime)
    payment_season = Column(String(300))
    payment_child_name = Column(String(300))
    payment_child_parent_name = Column(String(300))
    payment_type = Column(String(300))
    payment_sum = Column(Float)
    payment_comment = Column(String(1000))
    record_short = Column(String(4000))


# Контекстный менеджер для работы с сессиями
@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def add_season(season_name, start_date, end_date):
    with session_scope() as session:
        new_season = Season(season_name=season_name, season_start_date=start_date, season_end_date=end_date)
        session.add(new_season)


def delete_season(season_id):
    with session_scope() as session:
        season = session.query(Season).filter_by(season_id=season_id).first()
        session.delete(season)


def update_season(season_id, new_data):
    with session_scope() as session:
        season = session.query(Season).filter_by(season_id=season_id).first()
        for key, value in new_data.items():
            setattr(season, key, value)


def add_filial(filial_name, season_id):
    with session_scope() as session:
        new_filial = Filial(filial_name=filial_name, season_id=season_id)
        session.add(new_filial)


def delete_filial(filial_id):
    with session_scope() as session:
        filial = session.query(Filial).filter_by(filial_id=filial_id).first()
        session.delete(filial)


def update_filial(filial_id, new_data):
    with session_scope() as session:
        filial = session.query(Filial).filter_by(filial_id=filial_id).first()
        for key, value in new_data.items():
            setattr(filial, key, value)


def add_group(group_name, group_size, start_date, end_date, season_id, filial_id, children_recorded, children_payed):
    with session_scope() as session:
        new_group = Group(
            group_name=group_name, group_size=group_size, group_start_date=start_date, group_end_date=end_date,
            season_id=season_id, filial_id=filial_id, children_recorded=children_recorded, children_payed=children_payed
        )
        session.add(new_group)


def delete_group(group_id):
    with session_scope() as session:
        group = session.query(Group).filter_by(group_id=group_id).first()
        session.delete(group)


def update_group(group_id, new_data):
    with session_scope() as session:
        group = session.query(Group).filter_by(group_id=group_id).first()
        for key, value in new_data.items():
            setattr(group, key, value)


def add_child(child_name, child_age, parent_name, parent_num, season_id, filial_id, group_id):
    with session_scope() as session:
        # Добавляем ребёнка
        new_child = Child(
            child_name=child_name,
            child_age=child_age,
            child_parent_name=parent_name,
            child_parent_num=parent_num,
            season_id=season_id,
            filial_id=filial_id,
            group_id=group_id
        )
        session.add(new_child)

        group = session.query(Group).filter_by(group_id=group_id).first()
        if group:
            group.children_recorded += 1  # Увеличиваем значение children_recorded на 1
            session.add(group)  # Обновляем объект группы в сессии


def delete_child(child_id):
    with session_scope() as session:
        child = session.query(Child).filter_by(child_id=child_id).first()
        session.delete(child)


def update_child(child_id, new_data):
    with session_scope() as session:
        child = session.query(Child).filter_by(child_id=child_id).first()
        for key, value in new_data.items():
            setattr(child, key, value)


def show_filials_for_season(season_id):
    with session_scope() as session:
        filials = session.query(Filial).filter_by(season_id=season_id).all()
        return [{'filial_id': filial.filial_id, 'filial_name': filial.filial_name} for filial in filials]


def show_groups_for_filial(filial_id):
    with session_scope() as session:
        groups = session.query(Group).filter_by(filial_id=filial_id).all()
        return [{'group_id': group.group_id, 'group_name': group.group_name} for group in groups]


def show_children_for_group(group_id):
    with session_scope() as session:
        children = session.query(Child).filter_by(group_id=group_id).all()
        return [{'child_id': child.child_id, 'child_name': child.child_name} for child in children]


def get_season_list():
    with session_scope() as session:
        seasons = session.query(Season).all()
        return [season.season_name for season in seasons]


def get_season_id_by_name(season_name):
    with session_scope() as session:
        season = session.query(Season).filter_by(season_name=season_name).first()
        if season:
            return season.season_id
        else:
            return None  # Если сезон с таким именем не найден


def get_season_data_by_id(season_id):
    with session_scope() as session:
        season = session.query(Season).filter_by(season_id=season_id).first()
        if season:
            return {
                'season_id': season.season_id,
                'season_name': season.season_name,
                'season_start_date': season.season_start_date,
                'season_end_date': season.season_end_date
            }
        else:
            return None  # Если сезон с таким ID не найден


def get_filials_list_for_season(season_id):
    with session_scope() as session:
        filials = session.query(Filial).filter_by(season_id=season_id).all()
        return [filial.filial_name for filial in filials]


def get_filials_groups_data_for_season(season_id):
    with session_scope() as session:
        filials_data = {}

        # Получаем все филиалы для указанного сезона
        filials = session.query(Filial).filter_by(season_id=season_id).all()

        for filial in filials:
            filial_name = filial.filial_name
            filials_data[filial_name] = {}

            # Получаем все группы для текущего филиала
            groups = session.query(Group).filter_by(filial_id=filial.filial_id).all()

            for group in groups:
                group_name = group.group_name
                filials_data[filial_name][group_name] = {
                    "group_size": group.group_size,
                    "children_recorded": group.children_recorded,
                    "children_payed": group.children_payed
                }

        return filials_data


def add_group_to_filial_in_season(group_name, group_size, start_date, end_date, season_id, filial_id,
                                  children_recorded=0, children_payed=0):
    with session_scope() as session:
        # Проверяем, существует ли филиал
        filial = session.query(Filial).filter_by(filial_id=filial_id, season_id=season_id).first()
        if not filial:
            raise ValueError(f"Филиал с ID {filial_id} не найден в сезоне {season_id}.")

        # Проверяем, существует ли сезон
        season = session.query(Season).filter_by(season_id=season_id).first()
        if not season:
            raise ValueError(f"Сезон с ID {season_id} не найден.")

        # Создаем новую группу
        new_group = Group(
            group_name=group_name,
            group_size=group_size,
            group_start_date=start_date,
            group_end_date=end_date,
            season_id=season_id,
            filial_id=filial_id,
            children_recorded=children_recorded,
            children_payed=children_payed
        )

        session.add(new_group)
        session.commit()


def get_filial_id_by_name_and_season(filial_name, season_id):
    with session_scope() as session:
        # Поиск филиала по имени и ID сезона
        filial = session.query(Filial).filter_by(filial_name=filial_name, season_id=season_id).first()

        if filial:
            return filial.filial_id
        else:
            raise ValueError(f"Филиал с именем '{filial_name}' в сезоне с ID {season_id} не найден.")


def get_groups_list_for_season_and_filial(season_id, filial_id):
    with session_scope() as session:
        # Получение списка групп для указанного сезона и филиала
        groups = session.query(Group).filter_by(season_id=season_id, filial_id=filial_id).all()

        # Формируем список с именами групп
        groups_list = [group.group_name for group in groups]

        return groups_list


def get_season_name_by_id(season_id):
    with session_scope() as session:
        season = session.query(Season).filter_by(season_id=season_id).first()
        return season.season_name


def get_filial_name_by_id(filial_id):
    with session_scope() as session:
        season = session.query(Filial).filter_by(filial_id=filial_id).first()
        return season.filial_name


def get_group_id(season_id, filial_id, group_name):
    with session_scope() as session:
        group = session.query(Group).filter_by(season_id=season_id, filial_id=filial_id, group_name=group_name).first()
        return group.group_id


def add_user_record(username, userpass, user_role):
    existing = get_user_list()
    if username not in existing:
        with session_scope() as session:
            new_record = UsersTable(user_name=username,
                                    user_password=userpass,
                                    user_role=user_role)
            session.add(new_record)


def delete_user_record(value):
    with session_scope() as session:
        record = session.query(UsersTable).filter_by(user_name=value).first()
        if record:
            session.delete(record)


def update_user_password(username, new_pass):
    with session_scope() as session:
        record = session.query(UsersTable).filter(UsersTable.user_name == username).first()
        if record:
            record.user_password = new_pass


def update_user_role(username, new_role):
    with session_scope() as session:
        record = session.query(UsersTable).filter(UsersTable.user_name == username).first()
        if record:
            record.user_role = new_role


def get_users_dataframe():
    return get_table_as_dataframe(UsersTable, columns_order=["user_name", "user_role"],
                                  on_error_text="Ошибка получения датафрейма пользователей")


def get_user_list():
    return get_list(UsersTable, 'user_name', "Ошибка при загрузке списка пользователей")


def check_user_password(user):
    with session_scope() as session:
        result = session.query(UsersTable.user_password).filter(UsersTable.user_name == user).first()
        return result[0] if result else None


def get_user_role(username):
    with session_scope() as session:
        result = session.query(UsersTable.user_role).filter(UsersTable.user_name == username).first()
        return result[0] if result else None


def get_info_list():
    return get_list(Info, 'child_name', "Ошибка при загрузке списка детей")


def get_info_for_group_addition(child_name):
    with session_scope() as session:
        result = session.query(Info.child_birthday, Info.parent_main, Info.phone_main).filter(
            Info.child_name == child_name).first()
        if result:
            return result.child_birthday, result.parent_main, result.phone_main
        return None


def get_child_list_for_parent(parent_name):
    with session_scope() as session:
        results = session.query(Child.child_name).filter(Child.child_parent_name == parent_name).all()
        return [result.child_name for result in results]


def add_info_record(email, child_name, child_birthday, parent_main, phone_main,
                    parent_add, phone_add, leave, additional_contact, addr,
                    disease, allergy, other, physic, swimm, jacket_swimm,
                    hobby, school, additional_info, departures, referer,
                    ok, mailing, personal_accept, oms):
    existing = get_info_list()
    if child_name not in existing:
        with session_scope() as session:
            new_record = Info(email=email,
                              child_name=child_name,
                              child_birthday=child_birthday,
                              parent_main=parent_main,
                              phone_main=phone_main,
                              parent_add=parent_add,
                              phone_add=phone_add,
                              leave=leave,
                              additional_contact=additional_contact,
                              addr=addr,
                              disease=disease,
                              allergy=allergy,
                              other=other,
                              physic=physic,
                              swimm=swimm,
                              jacket_swimm=jacket_swimm,
                              hobby=hobby,
                              school=school,
                              additional_info=additional_info,
                              departures=departures,
                              referer=referer,
                              ok=ok,
                              mailing=mailing,
                              personal_accept=personal_accept,
                              oms=oms)
            session.add(new_record)


def get_info_dataframe():
    return get_table_as_dataframe(Info, columns_order=["email", "child_name", "child_birthday", "parent_main",
                                                       "phone_main", "parent_add", "phone_add", "leave",
                                                       "additional_contact", "addr", "disease", "allergy", "other",
                                                       "physic", "swimm", "jacket_swimm", "hobby", "school",
                                                       "additional_info", "departures", "referer", "ok", "mailing",
                                                       "personal_accept", "oms"],
                                  on_error_text="Ошибка получения датафрейма анкет")


def show_group_card(season_id, filial_id, group_id):
    with session_scope() as session:
        try:
            result = session.query(Child).filter_by(season_id=season_id, filial_id=filial_id,
                                                    group_id=group_id).all()
            if not result:
                return pd.DataFrame()

            dataframe = pd.DataFrame([item.__dict__ for item in result])
            dataframe.drop(columns='_sa_instance_state', inplace=True)
            return dataframe
        except Exception as e:
            return pd.DataFrame()


def get_payments_dataframe():
    return get_table_as_dataframe(Payments, columns_order=["payment_creation_time",
                                                           'worker_login',
                                                           "payment_child_parent_name",
                                                           "payment_child_name",
                                                           "payment_sum",
                                                           "payment_type",
                                                           "payment_season",
                                                           "payment_comment"],
                                  on_error_text="Ошибка получения датафрейма приходов")


def get_payments_for_single_child(child_name):
    return get_table_as_dataframe(Payments, columns_order=["payment_creation_time",
                                                           'worker_login',
                                                           "payment_child_parent_name",
                                                           "payment_child_name",
                                                           "payment_sum",
                                                           "payment_type",
                                                           "payment_season",
                                                           "payment_comment"],
                                  column=Payments.payment_child_name,
                                  column_value=child_name,
                                  on_error_text="Ошибка получения датафрейма приходов")


def get_payments_for_single_adult(adult_name):
    return get_table_as_dataframe(Payments, columns_order=["payment_creation_time",
                                                           'worker_login',
                                                           "payment_child_parent_name",
                                                           "payment_child_name",
                                                           "payment_sum",
                                                           "payment_type",
                                                           "payment_season",
                                                           "payment_comment"],
                                  column=Payments.payment_child_parent_name,
                                  column_value=adult_name,
                                  on_error_text="Ошибка получения датафрейма приходов")


def get_parent_list():
    return get_list(Child, 'child_parent_name', "Ошибка при загрузке списка родителей")


def add_payment(login, season, child_name, parent_name, paytype, summa, comment):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record_short = f"{login}: приход {summa} ({paytype}) от {parent_name} за {child_name} {season} ({comment})"
    with session_scope() as session:
        new_record = Payments(worker_login=login,
                              payment_creation_time=now,
                              payment_season=season,
                              payment_child_name=child_name,
                              payment_child_parent_name=parent_name,
                              payment_type=paytype,
                              payment_sum=summa,
                              payment_comment=comment,
                              record_short=record_short)
        session.add(new_record)


# Инициализация базы данных
engine = create_engine(sql_connection_string)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
