from sqlalchemy import Column, Integer, String, Date, Boolean
from .database import Base
from datetime import date



#Создание таблицы пользователей в БД
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    department = Column(String, nullable=False)
    position = Column(String, nullable=False)



#Создание таблицы заявок в БД
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    urgent = Column(Boolean, default= False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="not started")
    client = Column(String, index=True, nullable=False)
    master = Column(String, index=True, nullable=False)