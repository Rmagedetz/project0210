import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import datetime
from connections import sql_connection_string
import time

Base = declarative_base()
engine = sqlalchemy.create_engine(sql_connection_string)
metadata = sqlalchemy.MetaData()
Session = sessionmaker(bind=engine)


def initiate_query(query, on_error_text):
    session = Session()

    try:
        session.add(query)
        session.commit()
        print("Запись добавлена успешно!")

    except Exception as e:
        session.rollback()
        print(f"{on_error_text} : {e}")

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
    print(f"Начало пакетной вставки {total_records} записей...")

    try:
        start_time = time.time()

        # Проходим по списку записей с шагом batch_size
        for i in range(0, total_records, batch_size):
            batch = queries[i:i + batch_size]
            session.add_all(batch)
            session.commit()

            # Отслеживание прогресса
            print(f"Вставлено {min(i + batch_size, total_records)} из {total_records} записей.")

        elapsed_time = time.time() - start_time
        print(f"Все записи добавлены успешно за {elapsed_time:.2f} секунд!")

    except Exception as e:
        session.rollback()
        print(f"{on_error_text} : {e}")
    finally:
        session.close()
        print("Сессия закрыта.")


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


def delete_single_record_by_column(cls, column_name, value, on_error_text):
    session = Session()

    try:
        column = getattr(cls, column_name, None)
        if column is None:
            raise ValueError(f"Столбец {column_name} не существует.")

        record = session.query(cls).filter(column == value).first()
        if record is None:
            raise ValueError(f"Запись с {column_name} = {value} не найдена.")

        session.delete(record)
        session.commit()
        print(f"Запись с {column_name} = {value} успешно удалена.")

    except Exception as e:
        session.rollback()
        print(f"{on_error_text}: столбец {column_name} = {value}: {e}")

    finally:
        session.close()


def delete_many_records_by_column(cls, column_name, value, on_error_text):
    session = Session()

    try:
        column = getattr(cls, column_name, None)
        if column is None:
            raise ValueError(f"Столбец {column_name} не существует.")

        records = session.query(cls).filter(column == value).all()
        if records is None:
            raise ValueError(f"Запись с {column_name} = {value} не найдена.")
        for record in records:
            session.delete(record)
        session.commit()
        print(f"Запись с {column_name} = {value} успешно удалена.")

    except Exception as e:
        session.rollback()
        print(f"{on_error_text}: столбец {column_name} = {value}: {e}")

    finally:
        session.close()


class UsersTable(Base):
    __tablename__ = "Users"
    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_name = sqlalchemy.Column(sqlalchemy.String(300))
    user_password = sqlalchemy.Column(sqlalchemy.String(100))
    user_role = sqlalchemy.Column(sqlalchemy.String(100))

    @classmethod
    def add_record(cls, username, userpass, user_role):
        existing = cls.get_list()
        if username not in existing:
            new_record = cls(user_name=username,
                             user_password=userpass,
                             user_role=user_role)
            initiate_query(new_record, on_error_text="Ошибка добавления пользователя")

    @classmethod
    def delete_record(cls, value):
        delete_single_record_by_column(cls, 'user_name', value, on_error_text="Ошибка удаления пользователя")

    @classmethod
    def update_password(cls, username, new_pass):
        session = Session()
        try:
            record = session.query(cls).filter(cls.user_name == username).first()
            if record is None:
                raise ValueError(f"Запись пользователя {username} не найдена")
            record.user_password = new_pass
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    @classmethod
    def update_role(cls, username, new_role):
        session = Session()
        try:
            record = session.query(cls).filter(cls.user_name == username).first()
            if record is None:
                raise ValueError(f"Запись пользователя {username} не найдена")
            record.user_role = new_role
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    @classmethod
    def get_as_dataframe(cls):
        return get_table_as_dataframe(cls, columns_order=["user_name", "user_role"],
                                      on_error_text="Ошибка получения датафрейма пользователей")

    @classmethod
    def get_list(cls):
        return get_list(cls, 'user_name', "Ошибка при загрузке списка пользователей")

    @classmethod
    def check_pass(cls, user):
        session = Session()
        try:
            result = session.query(cls.user_password).filter(cls.user_name == user).first()
            return result[0]
        except Exception as e:
            print(f"Ошибка при проверке пароля: {e}")
            return []
        finally:
            session.close()

    @classmethod
    def get_role(cls, username):
        session = Session()
        try:
            result = session.query(cls.user_role).filter(cls.user_name == username).first()
            return result[0]
        except Exception as e:
            print(f"Ошибка при проверке роли: {e}")
            return []
        finally:
            session.close()


class Group(Base):
    __tablename__ = "groups"
    group_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    group_name = sqlalchemy.Column(sqlalchemy.String(300))
    season = sqlalchemy.Column(sqlalchemy.String(300))
    filial = sqlalchemy.Column(sqlalchemy.String(300))
    start_date = sqlalchemy.Column(sqlalchemy.Date)
    end_date = sqlalchemy.Column(sqlalchemy.Date)
    children_count = sqlalchemy.Column(sqlalchemy.Integer)

    @classmethod
    def get_list(cls):
        return get_list(cls, 'group_name', "Ошибка при загрузке списка групп")

    @classmethod
    def add_group(cls, group_name, season, filial, start_date, end_date, children_count):
        existing = cls.get_list()
        if group_name not in existing:
            new_record = cls(group_name=group_name,
                             season=season,
                             filial=filial,
                             start_date=start_date,
                             end_date=end_date,
                             children_count=children_count)
            initiate_query(new_record, on_error_text="Ошибка добавления группы")

    @classmethod
    def get_as_dataframe(cls):
        return get_table_as_dataframe(cls, columns_order=["filial", 'group_name', "start_date", "end_date"],
                                      on_error_text="Ошибка получения датафрейма групп по филиалу")

    @classmethod
    def delete_record_by_filial(cls, value):
        delete_many_records_by_column(cls, "filial", value=value, on_error_text="Ошибка удаления групп")

    @classmethod
    def request_children_quantity(cls, season, filial, group):
        session = Session()
        try:
            result = session.query(cls.children_count).filter(cls.season == season,
                                                              cls.filial == filial,
                                                              cls.group_name == group).first()
            return result[0]
        except Exception as e:
            print(f"Ошибка при получении количества детей: {e}")
            return []
        finally:
            session.close()

    @classmethod
    def get_groups_list_for_season_and_filial(cls, season, filial):
        session = Session()
        try:
            result = session.query(cls.group_name).filter(cls.season == season,
                                                          cls.filial == filial).all()
            return [x[0] for x in result]
        except Exception as e:
            print(f"Ошибка при получении количества детей: {e}")
            return []
        finally:
            session.close()


class Filial(Base):
    __tablename__ = "filials"
    filial_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    season = sqlalchemy.Column(sqlalchemy.String(300))
    filial_name = sqlalchemy.Column(sqlalchemy.String(300))

    @classmethod
    def get_list(cls):
        return get_list(cls, 'filial_name', "Ошибка при загрузке списка филиалов")

    @classmethod
    def add_record(cls, filial_name, season):
        existing = cls.get_list()
        if filial_name not in existing:
            new_record = cls(filial_name=filial_name, season=season)
            initiate_query(new_record, on_error_text="Ошибка добавления филиала")

    @classmethod
    def delete_record(cls, value):
        delete_single_record_by_column(cls, 'filial_name', value, on_error_text="Ошибка удаления филиала")
        Group.delete_record_by_filial(value)

    @classmethod
    def get_filial_list_for_season(cls, season_name):
        session = Session()

        try:
            results = session.query(cls.filial_name).filter(cls.season == season_name).all()
            return [result.filial_name for result in results]

        except Exception as e:
            print(f"Ошибка при получении значений столбца Receipt_type_name: {e}")
            return []

        finally:
            session.close()


class Season(Base):
    __tablename__ = "seasons"
    season_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    season_name = sqlalchemy.Column(sqlalchemy.String(200))
    season_start = sqlalchemy.Column(sqlalchemy.Date)
    season_end = sqlalchemy.Column(sqlalchemy.Date)

    @classmethod
    def get_list(cls):
        return get_list(cls, 'season_name', "Ошибка при загрузке списка филиалов")

    @classmethod
    def add_record(cls, season_name, season_start, season_end):
        existing = cls.get_list()
        if season_name not in existing:
            new_record = cls(season_name=season_name,
                             season_start=season_start,
                             season_end=season_end)
            initiate_query(new_record, on_error_text="Ошибка добавления сезона")

    @classmethod
    def delete_record(cls, value):
        delete_single_record_by_column(cls, 'season_name', value, on_error_text="Ошибка удаления сезона")
        Group.delete_record_by_filial(value)


class Children(Base):
    __tablename__ = "children"
    child_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    child_name = sqlalchemy.Column(sqlalchemy.String(300))
    child_age = sqlalchemy.Column(sqlalchemy.Integer)
    child_parent_name = sqlalchemy.Column(sqlalchemy.String(300))
    child_parent_phone_num = sqlalchemy.Column(sqlalchemy.String(300))
    child_season = sqlalchemy.Column(sqlalchemy.String(300))
    child_filial = sqlalchemy.Column(sqlalchemy.String(300))
    child_group = sqlalchemy.Column(sqlalchemy.String(300))

    @classmethod
    def get_list(cls):
        return get_list(cls, 'child_name', "Ошибка при загрузке списка филиалов")

    @classmethod
    def get_parent_list(cls):
        return get_list(cls, 'child_parent_name', "Ошибка при загрузке списка филиалов")

    @classmethod
    def add_record(cls, child_name, child_age, child_parent_name, child_parent_phone_num,
                   child_season, child_filial, child_group):
        existing = cls.get_list()
        if child_name not in existing:
            new_record = cls(child_name=child_name,
                             child_age=child_age,
                             child_parent_name=child_parent_name,
                             child_parent_phone_num=child_parent_phone_num,
                             child_season=child_season,
                             child_filial=child_filial,
                             child_group=child_group)
            initiate_query(new_record, on_error_text="Ошибка добавления ребенка")

    @classmethod
    def delete_record(cls, value):
        delete_single_record_by_column(cls, 'child_name', value, on_error_text="Ошибка удаления ребенка")
        Group.delete_record_by_filial(value)

    @classmethod
    def request_children_recorded(cls, season, filial, group):
        session = Session()
        try:
            result = session.query(cls.child_name).filter(cls.child_season == season,
                                                          cls.child_filial == filial,
                                                          cls.child_group == group).all()
            return len(result)
        except Exception as e:
            print(f"Ошибка при получении количества детей: {e}")
            return []
        finally:
            session.close()

    @classmethod
    def show_group_card(cls, season, filial, group):
        session = Session()
        try:
            result = session.query(cls).filter(cls.child_season == season,
                                               cls.child_filial == filial,
                                               cls.child_group == group).all()
            dataframe = pd.DataFrame([item.__dict__ for item in result])
            dataframe.drop(columns='_sa_instance_state', inplace=True)
            return dataframe
        except Exception as e:
            print(f"Пустая карточка группы: {e}")
            return []
        finally:
            session.close()

    @classmethod
    def get_child_list_for_parent(cls, parent_name):
        session = Session()

        try:
            results = session.query(cls.child_name).filter(cls.child_parent_name == parent_name).all()
            return [result.child_name for result in results]

        except Exception as e:
            print(f"Ошибка при получении списка детей для родителя: {e}")
            return []

        finally:
            session.close()


class Payments(Base):
    __tablename__ = "payments"
    payment_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    worker_login = sqlalchemy.Column(sqlalchemy.String(300))
    payment_creation_time = sqlalchemy.Column(sqlalchemy.DateTime)
    payment_season = sqlalchemy.Column(sqlalchemy.String(300))
    payment_child_name = sqlalchemy.Column(sqlalchemy.String(300))
    payment_child_parent_name = sqlalchemy.Column(sqlalchemy.String(300))
    payment_type = sqlalchemy.Column(sqlalchemy.String(300))
    payment_sum = sqlalchemy.Column(sqlalchemy.Float)
    payment_comment = sqlalchemy.Column(sqlalchemy.String(1000))
    record_short = sqlalchemy.Column(sqlalchemy.String(4000))

    @classmethod
    def get_list(cls):
        return get_list(cls, 'record_short', "Ошибка при загрузке списка оплат")

    @classmethod
    def add_record(cls, login, season, child_name, parent_name, paytype, summa, comment):
        existing = cls.get_list()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_short = f"{login}: приход {summa} ({paytype}) от {parent_name} за {child_name} {season} ({comment})"
        if record_short not in existing:
            new_record = cls(worker_login=login,
                             payment_creation_time=now,
                             payment_season=season,
                             payment_child_name=child_name,
                             payment_child_parent_name=parent_name,
                             payment_type=paytype,
                             payment_sum=summa,
                             payment_comment=comment,
                             record_short=record_short)
            initiate_query(new_record, on_error_text="Ошибка добавления прихода")

    @classmethod
    def delete_record(cls, value):
        delete_single_record_by_column(cls, 'record_short', value, on_error_text="Ошибка удаления прихода")

    @classmethod
    def get_as_dataframe(cls):
        return get_table_as_dataframe(cls, columns_order=["payment_creation_time",
                                                          'worker_login',
                                                          "payment_child_parent_name",
                                                          "payment_child_name",
                                                          "payment_sum",
                                                          "payment_type",
                                                          "payment_season",
                                                          "payment_comment"],
                                      on_error_text="Ошибка получения датафрейма приходов")

    @classmethod
    def get_as_dataframe_for_single_child(cls, value):
        column = cls.payment_child_name
        return get_table_as_dataframe(cls, columns_order=["payment_creation_time",
                                                          'worker_login',
                                                          "payment_child_parent_name",
                                                          "payment_child_name",
                                                          "payment_sum",
                                                          "payment_type",
                                                          "payment_season",
                                                          "payment_comment"],
                                      on_error_text="Ошибка получения датафрейма приходов",
                                      column=column,
                                      column_value=value)

    @classmethod
    def get_as_dataframe_for_single_adult(cls, value):
        column = cls.payment_child_parent_name
        return get_table_as_dataframe(cls, columns_order=["payment_creation_time",
                                                          'worker_login',
                                                          "payment_child_parent_name",
                                                          "payment_child_name",
                                                          "payment_sum",
                                                          "payment_type",
                                                          "payment_season",
                                                          "payment_comment"],
                                      on_error_text="Ошибка получения датафрейма приходов",
                                      column=column,
                                      column_value=value)


class Info(Base):
    __tablename__ = "info"
    info_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String(300))
    child_name = sqlalchemy.Column(sqlalchemy.String(300))
    child_birthday = sqlalchemy.Column(sqlalchemy.String(300))
    parent_main = sqlalchemy.Column(sqlalchemy.String(300))
    phone_main = sqlalchemy.Column(sqlalchemy.String(300))
    parent_add = sqlalchemy.Column(sqlalchemy.String(300))
    phone_add = sqlalchemy.Column(sqlalchemy.String(300))
    leave = sqlalchemy.Column(sqlalchemy.String(300))
    additional_contact = sqlalchemy.Column(sqlalchemy.String(300))
    addr = sqlalchemy.Column(sqlalchemy.String(300))
    disease = sqlalchemy.Column(sqlalchemy.String(300))
    allergy = sqlalchemy.Column(sqlalchemy.String(300))
    other = sqlalchemy.Column(sqlalchemy.String(300))
    physic = sqlalchemy.Column(sqlalchemy.String(300))
    swimm = sqlalchemy.Column(sqlalchemy.String(300))
    jacket_swimm = sqlalchemy.Column(sqlalchemy.String(300))
    hobby = sqlalchemy.Column(sqlalchemy.String(300))
    school = sqlalchemy.Column(sqlalchemy.String(300))
    additional_info = sqlalchemy.Column(sqlalchemy.String(2000))
    departures = sqlalchemy.Column(sqlalchemy.String(300))
    referer = sqlalchemy.Column(sqlalchemy.String(300))
    ok = sqlalchemy.Column(sqlalchemy.String(300))
    mailing = sqlalchemy.Column(sqlalchemy.String(300))
    personal_accept = sqlalchemy.Column(sqlalchemy.String(300))
    oms = sqlalchemy.Column(sqlalchemy.String(300))

    @classmethod
    def get_list(cls):
        return get_list(cls, 'child_name', "Ошибка при загрузке списка детей")

    @classmethod
    def get_data_for_group_addition(cls, child_name):
        session = Session()
        try:
            result = session.query(cls.child_birthday, cls.parent_main, cls.phone_main).filter(
                cls.child_name == child_name).first()

            if result is None:
                return None

            return result.child_birthday, result.parent_main, result.phone_main
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            session.close()

    @classmethod
    def add_record(cls, email, child_name, child_birthday, parent_main, phone_main,
                   parent_add, phone_add, leave, additional_contact, addr,
                   disease, allergy, other, physic, swimm, jacket_swimm,
                   hobby, school, additional_info, departures, referer,
                   ok, mailing, personal_accept, oms):
        existing = cls.get_list()
        if child_name not in existing:
            new_record = cls(email=email,
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
            initiate_query(new_record, on_error_text="Ошибка добавления прихода")

    @classmethod
    def get_as_dataframe(cls):
        return get_table_as_dataframe(cls, columns_order=["email", "child_name", "child_birthday", "parent_main",
                                                          "phone_main",
                                                          "parent_add", "phone_add", "leave", "additional_contact",
                                                          "addr",
                                                          "disease", "allergy", "other", "physic", "swimm",
                                                          "jacket_swimm",
                                                          "hobby", "school", "additional_info", "departures", "referer",
                                                          "ok", "mailing", "personal_accept", "oms"],
                                      on_error_text="Ошибка получения датафрейма приходов")


Base.metadata.create_all(engine)
