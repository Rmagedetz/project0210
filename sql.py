from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
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


class Role(Base):
    __tablename__ = 'roles'

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(300), unique=True, nullable=False)

    creating_roles = Column(Boolean, default=False)
    editing_roles = Column(Boolean, default=False)
    deleting_roles = Column(Boolean, default=False)

    creating_users = Column(Boolean, default=False)
    editing_users = Column(Boolean, default=False)
    deleting_users = Column(Boolean, default=False)

    adding_seasons = Column(Boolean, default=False)
    editing_seasons = Column(Boolean, default=False)
    deleting_seasons = Column(Boolean, default=False)

    adding_filials = Column(Boolean, default=False)
    editing_filials = Column(Boolean, default=False)
    deleting_filials = Column(Boolean, default=False)

    adding_groups = Column(Boolean, default=False)
    editing_groups = Column(Boolean, default=False)
    deleting_groups = Column(Boolean, default=False)

    adding_leavers = Column(Boolean, default=False)
    editing_leavers = Column(Boolean, default=False)
    deleting_leavers = Column(Boolean, default=False)

    adding_payments = Column(Boolean, default=False)
    editing_payments = Column(Boolean, default=False)
    deleting_payments = Column(Boolean, default=False)

    adding_cancelations = Column(Boolean, default=False)
    editing_cancelations = Column(Boolean, default=False)
    deleting_cancelations = Column(Boolean, default=False)

    users = relationship(
        "User",
        back_populates="user_role",
        cascade="save-update",
        passive_deletes=True
    )


def add_role(role_name, **permissions):
    with session_scope() as session:
        new_role = Role(role_name=role_name, **permissions)
        session.add(new_role)
        session.commit()


def get_role_names():
    with session_scope() as session:
        roles = session.query(Role.role_name).filter(Role.role_name != 'superadmin').all()
        return [role[0] for role in roles]


def delete_role(role_name):
    with session_scope() as session:
        role = session.query(Role).filter_by(role_name=role_name).first()
        if not role:
            raise ValueError(f"Роль с именем '{role_name}' не найдена.")

        try:
            session.delete(role)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Невозможно удалить роль '{role_name}', так как к ней привязаны пользователи.")

        return f"Роль '{role_name}' успешно удалена."


def get_roles_dataframe():
    with session_scope() as session:
        roles = session.query(
            Role.role_name,
            Role.creating_roles,
            Role.editing_roles,
            Role.deleting_roles,
            Role.creating_users,
            Role.editing_users,
            Role.deleting_users,
            Role.adding_seasons,
            Role.editing_seasons,
            Role.deleting_seasons,
            Role.adding_filials,
            Role.editing_filials,
            Role.deleting_filials,
            Role.adding_groups,
            Role.editing_groups,
            Role.deleting_groups,
            Role.adding_leavers,
            Role.editing_leavers,
            Role.deleting_leavers,
            Role.adding_payments,
            Role.editing_payments,
            Role.deleting_payments,
            Role.adding_cancelations,
            Role.editing_cancelations,
            Role.deleting_cancelations,
        ).filter(Role.role_name != 'superadmin').all()

        df = pd.DataFrame(roles)

        df.index = df.index + 1

        return df


def update_role(role_name, new_data):
    with session_scope() as session:
        record = session.query(Role).filter_by(role_name=role_name).first()
        for key, value in new_data.items():
            setattr(record, key, value)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)

    user_role = relationship("Role", back_populates="users")


def get_user_list():
    return get_list(User, "user_name", "Ошибка загрузки списка пользователей")


def check_user_password(username):
    with session_scope() as session:
        result = session.query(User.password).filter(User.user_name == username).first()
        return result[0] if result else None


def get_user_role(username):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            raise ValueError(f"Пользователь {username} не найден.")

        return user.user_role.role_name


def get_users_dataframe():
    with session_scope() as session:
        users = session.query(User.user_name, Role.role_name).join(Role).filter(User.user_name != "superadmin").all()
        df = pd.DataFrame(users, columns=["User Name", "Role Name"])
        return df


def add_user(user_name, password, role_name):
    with session_scope() as session:
        role = session.query(Role).filter_by(role_name=role_name).first()
        if not role:
            raise ValueError("Роль с таким именем не найдена.")
        new_user = User(user_name=user_name, password=password, role_id=role.role_id)
        session.add(new_user)


def delete_user_record(value):
    with session_scope() as session:
        record = session.query(User).filter_by(user_name=value).first()
        if record:
            session.delete(record)


def update_user_password(username, new_data):
    with session_scope() as session:
        record = session.query(User).filter(User.user_name == username).first()
        for key, value in new_data.items():
            setattr(record, key, value)


def update_user_role(user_name, role_name):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=user_name).first()
        if not user:
            raise ValueError(f"Пользователь с именем '{user_name}' не найден.")

        role = session.query(Role).filter_by(role_name=role_name).first()
        if not role:
            raise ValueError(f"Роль с именем '{role_name}' не найдена.")

        # Обновление роли пользователя
        user.role_id = role.role_id
        session.add(user)
        session.commit()


def check_user_rights(username, right):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            raise ValueError(f"Пользователь {username} не найден.")

        user_role = user.user_role
        if hasattr(user_role, right):
            return getattr(user_role, right)
        else:
            raise ValueError(f"Право {right} не найдено в роли {user_role.role_name}.")


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    filials = relationship("Filial", back_populates="season")


def get_seasons_dataframe():
    with session_scope() as session:
        seasons = session.query(
            Season.name,
            Season.start_date,
            Season.end_date
        ).all()

        df = pd.DataFrame(seasons)

        df.index += 1

        return df


def get_seasons_list():
    return get_list(Season, "name", "Ошибка загрузки списка сезонов")


def add_season(name, start_date, end_date):
    with session_scope() as session:
        existing_season = session.query(Season).filter_by(name=name).first()
        if existing_season:
            raise ValueError("Сезон с таким именем уже существует.")
        new_season = Season(name=name, start_date=start_date, end_date=end_date)
        session.add(new_season)
        session.commit()


def delete_season(season_name):
    with session_scope() as session:
        season_to_delete = session.query(Season).filter(Season.name == season_name).first()

        if not season_to_delete:
            raise ValueError(f"Сезон с именем '{season_name}' не найден.")

        session.delete(season_to_delete)
        session.commit()


def update_season(season_name, new_data):
    with session_scope() as session:
        record = session.query(Season).filter(Season.name == season_name).first()
        for key, value in new_data.items():
            setattr(record, key, value)


class Filial(Base):
    __tablename__ = 'filials'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)

    season = relationship("Season", back_populates="filials")
    groups = relationship("Group", back_populates="filial")

    __table_args__ = (UniqueConstraint('name', 'season_id', name='_filial_season_uc'),)


def show_filials_for_season(season_name):
    with session_scope() as session:
        season = session.query(Season).filter_by(name=season_name).first()

        # Проверяем, существует ли сезон
        if not season:
            raise ValueError(f"Сезон с именем '{season_name}' не найден.")

        filials = session.query(Filial.name).filter_by(season_id=season.id).all()

        df = pd.DataFrame(filials)

        df.index += 1

        return df


def add_filial(season_name, filial_name):
    with session_scope() as session:
        season = session.query(Season).filter_by(name=season_name).first()

        if not season:
            raise ValueError(f"Сезон с именем '{season_name}' не найден.")

        existing_filial = session.query(Filial).filter_by(name=filial_name, season_id=season.id).first()
        if existing_filial:
            raise ValueError(f"Филиал с именем '{filial_name}' уже существует в сезоне '{season_name}'.")

        new_filial = Filial(name=filial_name, season_id=season.id)

        session.add(new_filial)
        session.commit()


def get_filials_list_for_season(season_name):
    with session_scope() as session:
        season = session.query(Season).filter_by(name=season_name).first()

        if not season:
            raise ValueError(f"Сезон с именем '{season_name}' не найден.")

        filials = session.query(Filial.name).filter_by(season_id=season.id).all()
        filial_names = [filial[0] for filial in filials]

        return filial_names


def delete_filial_from_season(season_name, filial_name):
    with session_scope() as session:
        season = session.query(Season).filter_by(name=season_name).first()

        if not season:
            raise ValueError(f"Сезон с именем '{season_name}' не найден.")

        filial = session.query(Filial).filter_by(name=filial_name, season_id=season.id).first()

        if not filial:
            raise ValueError(f"Филиал с именем '{filial_name}' не найден в сезоне '{season_name}'.")

        session.delete(filial)
        session.commit()


def rename_filial(season_name, filial_name, new_filial_name):
    with session_scope() as session:
        season = session.query(Season).filter_by(name=season_name).first()

        if not season:
            raise ValueError(f"Сезон с именем '{season_name}' не найден.")

        filial = session.query(Filial).filter_by(name=filial_name, season_id=season.id).first()

        if not filial:
            raise ValueError(f"Филиал с именем '{filial_name}' не найден в сезоне '{season_name}'.")

        existing_filial = session.query(Filial).filter_by(name=new_filial_name, season_id=season.id).first()
        if existing_filial:
            raise ValueError(f"Филиал с именем '{new_filial_name}' уже существует в сезоне '{season_name}'.")

        filial.name = new_filial_name
        session.commit()


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    filial_id = Column(Integer, ForeignKey('filials.id'), nullable=False)

    filial = relationship("Filial", back_populates="groups")
    children = relationship("GroupChild", back_populates="group")
    bills = relationship("Bills", back_populates="group")

    __table_args__ = (UniqueConstraint('name', 'filial_id', name='_group_filial_uc'),)


def get_groups_dataframe_for_filial_in_season(season_name, filial_name):
    with session_scope() as session:
        groups = session.query(
            Group.name,
            Group.capacity,
            Group.start_date,
            Group.end_date
        ).join(Filial, Group.filial_id == Filial.id
               ).join(Season, Group.season_id == Season.id
                      ).filter(
            Season.name == season_name,
            Filial.name == filial_name
        ).all()

        df = pd.DataFrame(groups)
        df.index += 1
        return df


def add_group_to_filial_in_season(season_name, filial_name, group_data):
    with session_scope() as session:
        season = session.query(Season).filter(Season.name == season_name).first()
        filial = session.query(Filial).filter(Filial.name == filial_name, Filial.season_id == season.id).first()

        new_group = Group(
            name=group_data['name'],
            capacity=group_data['capacity'],
            start_date=group_data['start_date'],
            end_date=group_data['end_date'],
            filial_id=filial.id,
            season_id=season.id
        )

        try:
            session.add(new_group)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def get_groups_list_for_filial_in_season(season_name, filial_name):
    with session_scope() as session:
        season = session.query(Season).filter(Season.name == season_name).first()
        if not season:
            return []

        filial = session.query(Filial).filter(Filial.name == filial_name, Filial.season_id == season.id).first()
        if not filial:
            return []

        groups = session.query(Group).filter(Group.filial_id == filial.id).all()
        return [group.name for group in groups]


def delete_group_from_filial_in_season(season_name, filial_name, group_name):
    with session_scope() as session:
        season = session.query(Season).filter(Season.name == season_name).first()
        if not season:
            return f"Сезон '{season_name}' не найден."

        filial = session.query(Filial).filter(Filial.name == filial_name, Filial.season_id == season.id).first()
        if not filial:
            return f"Филиал '{filial_name}' не найден в сезоне '{season_name}'."

        group = session.query(Group).filter(Group.name == group_name, Group.filial_id == filial.id).first()
        if not group:
            return f"Группа '{group_name}' не найдена в филиале '{filial_name}' в сезоне '{season_name}'."

        session.delete(group)
        session.commit()
        return f"Группа '{group_name}' успешно удалена из филиала '{filial_name}' в сезоне '{season_name}'."


def edit_group_data_in_filial_season(season_name, filial_name, group_name, new_group_data):
    with session_scope() as session:
        season = session.query(Season).filter(Season.name == season_name).first()
        if not season:
            return f"Сезон '{season_name}' не найден."

        filial = session.query(Filial).filter(Filial.name == filial_name, Filial.season_id == season.id).first()
        if not filial:
            return f"Филиал '{filial_name}' не найден в сезоне '{season_name}'."

        group = session.query(Group).filter(Group.name == group_name, Group.filial_id == filial.id,
                                            Group.season_id == season.id).first()
        if not group:
            return f"Группа '{group_name}' не найдена в филиале '{filial_name}' в сезоне '{season_name}'."

        group.name = new_group_data['name']
        group.capacity = new_group_data['capacity']
        group.start_date = new_group_data['start_date']
        group.end_date = new_group_data['end_date']

        try:
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


class Child(Base):
    __tablename__ = 'children'

    # базовые данные
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    parent_main_name = Column(String(50), nullable=False)
    parent_main_phone = Column(String(50), nullable=False)

    # анкетные данные
    email = Column(String(100), nullable=True, default="")
    child_birthday = Column(Date, nullable=True, default=None)
    parent_add = Column(String(50), nullable=True, default="")
    phone_add = Column(String(20), nullable=True, default="")
    leave = Column(String(3), nullable=True, default="")
    additional_contact = Column(String(100), nullable=True, default="")
    addr = Column(String(200), nullable=True, default="")
    disease = Column(String(100), nullable=True, default="")
    allergy = Column(String(100), nullable=True, default="")
    other = Column(String(100), nullable=True, default="")
    physic = Column(String(10), nullable=True, default="")
    swimm = Column(String(10), nullable=True, default="")
    jacket_swimm = Column(String(10), nullable=True, default="")
    hobby = Column(String(100), nullable=True, default="")
    school = Column(String(100), nullable=True, default="")
    additional_info = Column(String(255), nullable=True, default="")
    departures = Column(String(10), nullable=True, default="")
    referer = Column(String(100), nullable=True, default="")
    ok = Column(String(10), nullable=True, default="")
    mailing = Column(String(10), nullable=True, default="")
    personal_accept = Column(String(10), nullable=True, default="")
    oms = Column(String(20), nullable=True, default="")

    # данные для договора
    parent_passport = Column(String(100), nullable=True, default="")
    parent_adress = Column(String(100), nullable=True, default="")

    groups = relationship("GroupChild", back_populates="child")
    payments = relationship("Payments", back_populates="child")
    bills = relationship("Bills", back_populates="child")

    __table_args__ = (UniqueConstraint('name', name='_child_name_uc'),)


def get_children_dataframe():
    with session_scope() as session:
        children = session.query(
            Child.name,
            Child.age,
            Child.parent_main_name,
            Child.parent_main_phone
        ).all()

        df = pd.DataFrame(children)
        df.index += 1
        return df


def get_children_list():
    with session_scope() as session:
        children = session.query(Child.name).all()

        return [child.name for child in children]


def add_leaver(child_data):
    with session_scope() as session:
        new_child = Child(
            name=child_data['name'],
            age=child_data['age'],
            parent_main_name=child_data['parent_main_name'],
            parent_main_phone=child_data['parent_main_phone']
        )

        try:
            session.add(new_child)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def update_child_quiz(child_name, new_data):
    with session_scope() as session:
        record = session.query(Child).filter(Child.name == child_name).first()
        for key, value in new_data.items():
            setattr(record, key, value)
    return True


def edit_child_data(child_name, updated_data):
    with session_scope() as session:
        child = session.query(Child).filter(Child.name == child_name).first()

        if child:
            child.name = updated_data.get('name', child.name)
            child.age = updated_data.get('age', child.age)
            child.parent_main_name = updated_data.get('parent_main_name', child.parent_main_name)
            child.parent_main_phone = updated_data.get('parent_main_phone', child.parent_main_phone)

            try:
                session.commit()
                return True
            except IntegrityError:
                session.rollback()
                return False
        else:
            return False


def get_all_child_data(name):
    with session_scope() as session:
        child = session.query(Child).filter(Child.name == name).first()
        return {key: value for key, value in child.__dict__.items() if not key.startswith('_')}


def delete_leaver(child_name):
    with session_scope() as session:
        child = session.query(Child).filter(Child.name == child_name).first()
        session.delete(child)
        session.commit()


class GroupChild(Base):
    __tablename__ = 'group_children'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    child_id = Column(Integer, ForeignKey('children.id'), nullable=False)

    group = relationship("Group", back_populates="children")
    child = relationship("Child", back_populates="groups")


def add_child_to_group(child_name, season_name, filial_name, group_name):
    with session_scope() as session:
        # Получаем данные сезона
        season = session.query(Season).filter(Season.name == season_name).first()
        if not season:
            return False, f"Сезон '{season_name}' не найден."

        # Получаем данные филиала в указанном сезоне
        filial = session.query(Filial).filter(Filial.name == filial_name, Filial.season_id == season.id).first()
        if not filial:
            return False, f"Филиал '{filial_name}' не найден в сезоне '{season_name}'."

        # Получаем данные группы в указанном филиале
        group = session.query(Group).filter(Group.name == group_name, Group.filial_id == filial.id).first()
        if not group:
            return False, f"Группа '{group_name}' не найдена в филиале '{filial_name}' и сезоне '{season_name}'."

        # Получаем данные ребенка
        child = session.query(Child).filter(Child.name == child_name).first()
        if not child:
            return False, f"Ребенок '{child_name}' не найден."

        # Проверяем, есть ли ребенок уже в группе
        existing_entry = session.query(GroupChild).filter_by(group_id=group.id, child_id=child.id).first()
        if existing_entry:
            return False, f"Ребенок '{child_name}' уже добавлен в группу '{group_name}'."

        # Создаем запись о добавлении ребенка в группу
        new_group_child = GroupChild(group_id=group.id, child_id=child.id)
        session.add(new_group_child)

        try:
            session.commit()
            return True, f"Ребенок '{child_name}' успешно добавлен в группу '{group_name}'."
        except IntegrityError:
            session.rollback()
            return False, "Произошла ошибка при добавлении ребенка в группу."


def get_groups_with_children_count_and_paid_by_season(season_name):
    with session_scope() as session:
        # Получаем указанный сезон по имени
        season = session.query(Season).filter(Season.name == season_name).first()

        if not season:
            return {}  # Возвращаем пустой словарь, если сезон не найден

        # Получаем все филиалы в данном сезоне
        filials = session.query(Filial).filter(Filial.season_id == season.id).all()

        # Создаем словарь для хранения результатов
        result = {}

        for filial in filials:
            filial_data = {}

            # Получаем все группы для каждого филиала
            groups = session.query(Group).filter(Group.filial_id == filial.id).all()

            for group in groups:
                # Получаем количество детей в группе
                children_count = session.query(GroupChild).filter(GroupChild.group_id == group.id).count()

                # Получаем количество уникальных детей с платежами
                paid_children_count = session.query(Payments.child_id).join(GroupChild,
                                                                            GroupChild.child_id == Payments.child_id) \
                    .filter(GroupChild.group_id == group.id) \
                    .distinct().count()

                # Рассчитываем оставшуюся вместимость группы
                remaining_capacity = group.capacity - children_count

                # Записываем данные по группе
                group_data = {
                    "group_name": group.name,
                    "children_count": children_count,
                    "paid_children_count": paid_children_count,
                    "capacity": group.capacity,
                    "remaining_capacity": remaining_capacity
                }

                filial_data[group.name] = group_data

            # Записываем данные по филиалу в результат
            result[filial.name] = filial_data

        # Возвращаем результат без ключа сезона
        return result


def get_children_in_group(season_name, filial_name, group_name):
    with session_scope() as session:
        # Получаем сезон по имени
        season = session.query(Season).filter(Season.name == season_name).first()
        if not season:
            return pd.DataFrame()  # Возвращаем пустой датафрейм, если сезон не найден

        # Получаем филиал по имени
        filial = session.query(Filial).filter(Filial.name == filial_name, Filial.season_id == season.id).first()
        if not filial:
            return pd.DataFrame()  # Возвращаем пустой датафрейм, если филиал не найден

        # Получаем группу по имени
        group = session.query(Group).filter(Group.name == group_name, Group.filial_id == filial.id).first()
        if not group:
            return pd.DataFrame()  # Возвращаем пустой датафрейм, если группа не найдена

        # Получаем всех детей в группе
        children = session.query(GroupChild).filter(GroupChild.group_id == group.id).all()

        # Если нет детей, возвращаем пустой датафрейм
        if not children:
            return pd.DataFrame()

        # Получаем данные по каждому ребенку
        children_data = []
        for group_child in children:
            child = session.query(Child).filter(Child.id == group_child.child_id).first()
            if child:
                children_data.append({column.name: getattr(child, column.name) for column in Child.__table__.columns})

        # Создаем датафрейм из собранных данных
        df = pd.DataFrame(children_data)
        df = df.drop("id", axis=1)
        df.index += 1
        return df


def remove_child_from_group(season_name, filial_name, group_name, child_name):
    with session_scope() as session:
        # Получаем идентификаторы сезона, филиала и группы
        season = session.query(Season).filter(Season.name == season_name).first()
        filial = session.query(Filial).filter(Filial.name == filial_name, Filial.season_id == season.id).first()
        group = session.query(Group).filter(Group.name == group_name, Group.filial_id == filial.id).first()

        # Получаем идентификатор ребенка
        child = session.query(Child).filter(Child.name == child_name).first()

        if not season or not filial or not group or not child:
            return False  # Возвращаем False, если один из элементов не найден

        # Удаляем запись о ребенке из группы
        try:
            # Предполагаем, что у вас есть промежуточная таблица GroupChild
            group_child = session.query(GroupChild).filter(GroupChild.group_id == group.id,
                                                           GroupChild.child_id == child.id).first()
            if group_child:
                session.delete(group_child)
                session.commit()
                return True  # Успешное удаление
            else:
                return False  # Если ребенка не было в группе
        except Exception as e:
            session.rollback()  # Откат изменений в случае ошибки
            print(f"Ошибка при удалении ребенка из группы: {e}")
            return False  # Возвращаем False при ошибке


def move_child_to_group(out_season_name, out_filial_name, out_group_name, child_name, in_season_name, in_filial_name,
                        in_group_name):
    with session_scope() as session:
        # Получаем исходящие идентификаторы сезона, филиала и группы
        out_season = session.query(Season).filter(Season.name == out_season_name).first()
        out_filial = session.query(Filial).filter(Filial.name == out_filial_name,
                                                  Filial.season_id == out_season.id).first()
        out_group = session.query(Group).filter(Group.name == out_group_name, Group.filial_id == out_filial.id).first()

        # Получаем входящие идентификаторы сезона, филиала и группы
        in_season = session.query(Season).filter(Season.name == in_season_name).first()
        in_filial = session.query(Filial).filter(Filial.name == in_filial_name,
                                                 Filial.season_id == in_season.id).first()
        in_group = session.query(Group).filter(Group.name == in_group_name, Group.filial_id == in_filial.id).first()

        # Получаем идентификатор ребенка
        child = session.query(Child).filter(Child.name == child_name).first()

        if not out_season or not out_filial or not out_group or not in_season or not in_filial or not in_group or not child:
            return False  # Возвращаем False, если один из элементов не найден

        # Удаляем запись о ребенке из исходящей группы
        try:
            group_child_out = session.query(GroupChild).filter(GroupChild.group_id == out_group.id,
                                                               GroupChild.child_id == child.id).first()
            if group_child_out:
                session.delete(group_child_out)  # Удаляем из исходящей группы

            # Добавляем запись о ребенке во входящую группу
            group_child_in = GroupChild(group_id=in_group.id, child_id=child.id)
            session.add(group_child_in)
            session.commit()
            return True  # Успешный перенос
        except Exception as e:
            session.rollback()  # Откат изменений в случае ошибки
            print(f"Ошибка при переносе ребенка: {e}")
            return False  # Возвращаем False при ошибке


class Payments(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    payment_date = Column(DateTime, nullable=False)
    child_id = Column(Integer, ForeignKey('children.id'), nullable=False)
    amount = Column(Float, nullable=False)
    recorded_by = Column(String(50), nullable=False)
    comment = Column(String(200), nullable=True)

    child = relationship("Child", back_populates="payments")


class Bills(Base):
    __tablename__ = 'bills'

    id = Column(Integer, primary_key=True)
    payment_date = Column(DateTime, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    child_id = Column(Integer, ForeignKey('children.id'), nullable=False)
    amount = Column(Float, nullable=False)
    recorded_by = Column(String(50), nullable=False)
    comment = Column(String(200), nullable=True)

    child = relationship("Child", back_populates="bills")
    group = relationship("Group", back_populates="bills")


def get_payments_dataframe():
    with session_scope() as session:
        # Выполняем запрос, включая связь с Child и User
        payments = (
            session.query(Payments)
            .options(joinedload(Payments.child))  # Загрузка связанных данных о ребенке
            .all()
        )

        # Создаем списки для формирования датафрейма
        payment_data = []
        for payment in payments:
            child = payment.child  # Получаем объект ребенка через связь
            payment_data.append({
                "id": payment.id,
                "payment_date": payment.payment_date,
                "user": payment.recorded_by,  # Имя пользователя, записавшего платеж
                "child_name": child.name,
                "payment_amount": payment.amount,
                "comment": payment.comment
            })

        # Создаем датафрейм
        df = pd.DataFrame(payment_data)
        df.index += 1

        return df


def get_bills_dataframe():
    with session_scope() as session:
        # Выполняем запрос, включая связь с Child и Group
        bills = (
            session.query(Bills)
            .options(
                joinedload(Bills.child),  # Загрузка связанных данных о ребенке
                joinedload(Bills.group)  # Загрузка связанных данных о группе
            )
            .all()
        )

        # Создаем список данных для формирования датафрейма
        bill_data = []
        for bill in bills:
            child = bill.child  # Получаем объект ребенка через связь
            group = bill.group  # Получаем объект группы через связь
            bill_data.append({
                "id": bill.id,
                "payment_date": bill.payment_date,
                "user": bill.recorded_by,  # Имя пользователя, записавшего счет
                "child_name": child.name,
                "group_name": group.name if group else None,  # Имя группы (если оно есть)
                "amount": bill.amount,  # Сумма счета
                "comment": bill.comment
            })

        # Создаем датафрейм
        df = pd.DataFrame(bill_data)
        df.index += 1  # Индексация с 1, а не с 0

        return df


def add_payment(payment_date, child_name, amount, user_name, comment):
    with session_scope() as session:
        # Находим ребенка по имени
        child = session.query(Child).filter(Child.name == child_name).first()

        if not child:
            return False  # Возвращаем False, если ребенок не найден

        # Создаем новый объект платежа
        new_payment = Payments(
            payment_date=payment_date,
            child_id=child.id,  # Используем ID найденного ребенка
            amount=amount,
            recorded_by=user_name,  # Имя пользователя, записавшего платеж
            comment=comment
        )

        try:
            session.add(new_payment)  # Добавляем новый платеж в сессию
            session.commit()  # Подтверждаем изменения
            return True  # Возвращаем True при успешном добавлении
        except IntegrityError:
            session.rollback()  # Откатываем изменения при ошибке
            return False  # Возвращаем False при ошибке


def add_bill(payment_date, child_name, group_name, amount, user_name, comment):
    with session_scope() as session:
        # Находим ребенка по имени
        child = session.query(Child).filter(Child.name == child_name).first()
        group = session.query(Group).filter(Group.name == group_name).first()

        if not child:
            return False  # Возвращаем False, если ребенок не найден

        # Создаем новый объект платежа
        new_payment = Bills(
            payment_date=payment_date,
            child_id=child.id,  # Используем ID найденного ребенка
            group_id=group.id,
            amount=amount,
            recorded_by=user_name,  # Имя пользователя, записавшего платеж
            comment=comment
        )

        try:
            session.add(new_payment)  # Добавляем новый платеж в сессию
            session.commit()  # Подтверждаем изменения
            return True  # Возвращаем True при успешном добавлении
        except IntegrityError:
            session.rollback()  # Откатываем изменения при ошибке
            return False  # Возвращаем False при ошибке


def get_payment_details(payment_id):
    with session_scope() as session:
        # Получаем информацию о платеже по ID
        payment = session.query(Payments).filter(Payments.id == payment_id).first()

        if not payment:
            return pd.DataFrame()  # Возвращаем пустой DataFrame, если платеж не найден

        # Получаем информацию о ребенке, связанном с платежом
        child = session.query(Child).filter(Child.id == payment.child_id).first()

        # Создаем словарь с данными о платеже
        payment_data = {
            "payment_id": payment.id,
            "payment_date": payment.payment_date,
            "child_name": child.name if child else "Неизвестный ребенок",
            "amount": payment.amount,
            "user_name": payment.recorded_by,
            "comment": payment.comment
        }

        # Преобразуем словарь в DataFrame
        payment_df = pd.DataFrame([payment_data])

        return payment_df


def get_bill_details(bill_id):
    with session_scope() as session:
        # Получаем информацию о платеже по ID
        bill = session.query(Bills).filter(Bills.id == bill_id).first()

        if not bill:
            return pd.DataFrame()  # Возвращаем пустой DataFrame, если платеж не найден

        # Получаем информацию о ребенке, связанном с платежом
        child = session.query(Child).filter(Child.id == bill.child_id).first()
        group = session.query(Group).filter(Group.id == bill.group_id).first()

        # Создаем словарь с данными о платеже
        payment_data = {
            "payment_id": bill.id,
            "payment_date": bill.payment_date,
            "child_name": child.name if child else "Неизвестный ребенок",
            "group_name": group.name if group else "Неизвестная группа",
            "amount": bill.amount,
            "user_name": bill.recorded_by,
            "comment": bill.comment
        }

        # Преобразуем словарь в DataFrame
        payment_df = pd.DataFrame([payment_data])

        return payment_df


def edit_payment_data(payment_id, payment_date=None, child_name=None, amount=None, comment=None):
    with session_scope() as session:
        payment_id = int(payment_id)
        payment = session.query(Payments).filter(Payments.id == payment_id).first()

        if not payment:
            return False

        if payment_date:
            payment.payment_date = payment_date
        if amount is not None:
            payment.amount = amount
        if comment:
            payment.comment = comment

        if child_name:
            child = session.query(Child).filter(Child.name == child_name).first()
            if child:
                payment.child_id = child.id
            else:
                return False

        session.commit()
        return True


def delete_payment(payment_id):
    with session_scope() as session:
        payment_id = int(payment_id)

        payment = session.query(Payments).filter(Payments.id == payment_id).first()

        if not payment:
            return False

        session.delete(payment)
        session.commit()

        return True


def get_group_id_by_name_and_season_and_filial(group_name, season_name, filial_name):
    with Session() as session:
        # Получаем сезон по имени
        season = session.query(Season).filter_by(name=season_name).first()
        if not season:
            raise ValueError(f"Сезон с именем {season_name} не найден.")

        # Получаем филиал по имени и сезону
        filial = session.query(Filial).filter_by(name=filial_name, season_id=season.id).first()
        if not filial:
            raise ValueError(f"Филиал с именем {filial_name} в сезоне {season_name} не найден.")

        # Получаем группу по имени и ID филиала
        group = session.query(Group).filter_by(name=group_name, filial_id=filial.id).first()
        if not group:
            raise ValueError(f"Группа с именем {group_name} в филиале {filial_name} не найдена.")

        # Возвращаем ID группы
        return group.id


def get_child_id_by_name(child_name):
    with Session() as session:
        # Ищем ребенка по имени
        child = session.query(Child).filter_by(name=child_name).first()

        # Если ребенок не найден, выбрасываем ошибку
        if not child:
            raise ValueError(f"Ребенок с именем {child_name} не найден.")

        # Возвращаем ID ребенка
        return child.id


class Visits(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    child_id = Column(Integer, ForeignKey('children.id'), nullable=False)
    day = Column(Integer)
    visit = Column(String(10))

    __table_args__ = (UniqueConstraint('group_id', 'child_id', 'day', name='_unique_visit'),)

    @classmethod
    def get_visits_dataframe_for_group(cls, group_name):
        with session_scope() as session:
            # Выполняем запрос с объединением таблиц Groups и Children
            results = session.query(
                Child.name.label("Имя ребенка"),
                cls.day.label("День"),
                cls.visit.label("Посещение")
            ).join(
                Child, cls.child_id == Child.id
            ).join(
                Group, cls.group_id == Group.id
            ).filter(
                Group.name == group_name  # Фильтруем по названию группы
            ).all()

            # Преобразуем результаты в DataFrame
            df = pd.DataFrame(results, columns=["Имя ребенка", "День", "Посещение"])

            if df.empty:
                return pd.DataFrame(columns=["Имя ребенка"] + list(range(1, 11)))

            # Пивотируем данные, чтобы получить дни как столбцы
            pivot_df = df.pivot(index="Имя ребенка", columns="День", values="Посещение").reset_index()

            # Упорядочиваем столбцы
            pivot_df.columns.name = None  # Убираем имя уровня колонок
            all_days = list(range(1, 11))  # Дни от 1 до 10
            for day in all_days:
                if day not in pivot_df.columns:
                    pivot_df[day] = pd.NA  # Добавляем отсутствующие дни как NaN

            pivot_df = pivot_df[["Имя ребенка"] + all_days]
            pivot_df.index += 1
            return pivot_df

    @classmethod
    def set_visit(cls, child_name, group_name, day, visit):
        with session_scope() as session:
            child = session.query(Child).filter(Child.name == child_name).first()
            group = session.query(Group).filter(Group.name == group_name).first()
            try:
                add = cls(group_id=group.id,
                          child_id=child.id,
                          day=day,
                          visit=visit)
                session.add(add)
            except:
                pass

    @classmethod
    def insert_or_update_visits(cls, df_melted):
        with session_scope() as session:
            # Перебираем строки DataFrame и вставляем или обновляем записи в таблице visits
            for _, row in df_melted.iterrows():
                group_id = row['group_id']
                child_id = row['child_id']
                day = row['day']
                visit = row['visit']

                # Пытаемся найти существующую запись
                existing_visit = session.query(cls).filter_by(
                    group_id=group_id, child_id=child_id, day=day).first()

                if existing_visit:
                    # Если запись существует, проверяем отличается ли visit
                    if existing_visit.visit != visit:
                        # Если отличается, обновляем запись
                        existing_visit.visit = visit
                else:
                    # Если записи нет, создаем новую
                    new_visit = cls(
                        group_id=group_id,
                        child_id=child_id,
                        day=day,
                        visit=visit
                    )
                    session.add(new_visit)

            # После завершения цикла коммитим изменения
            session.commit()


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


engine = create_engine(sql_connection_string)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
