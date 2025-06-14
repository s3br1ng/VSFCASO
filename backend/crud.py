from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from typing import Optional

#Используется для хэширования паролей 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Поиск пользователя по нику
def get_user_by_nickname(db: Session, nickname: str):
    return db.query(models.User).filter(models.User.nickname == nickname).first()

#Создание нового пользователя в бд
def create_user(db: Session, user: schemas.Register):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(nickname=user.nickname, 
                          password_hash=hashed_password, 
                          role = user.role, 
                          last_name = user.last_name, 
                          first_name = user.first_name, 
                          patronymic = user.patronymic, 
                          date_of_birth = user.date_of_birth,
                          department = user.department, 
                          position = user.position)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#Проверка введенного пароля с действующим паролем
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

#Вход пользователя. Если пользователь не найден или пароль несовпадает, то возвращает none
def authenticate_user(db: Session, nickname: str, password: str):
    user = get_user_by_nickname(db, nickname)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

#Возвращает все заявки
def get_Orders(db: Session):
    return db.query(models.Order)

#Создает новую заявку
def create_Order(db: Session, Order: schemas.OrderBase, current_user: models.User):
    client_full_name = f"{current_user.last_name} {current_user.first_name} {current_user.patronymic}"
    
    # Создаем объект заявки, заменяя client на ФИО пользователя
    db_Order = models.Order(
        name=Order.name,
        urgent=Order.urgent,
        description=Order.description,
        status=Order.status or "not started",
        client=client_full_name,  # <-- здесь автоматически подставляем ФИО
        master=Order.master
    )
    
    db.add(db_Order)
    db.commit()
    db.refresh(db_Order)
    return db_Order

#Поиск заявки по id
def get_Order_by_id(db: Session, Order_id: int):
    return db.query(models.Order).filter(models.Order.id == Order_id).first()

#Обновление существующеё заявки
def update_Order(
    db: Session, 
    Order_id: int, 
    updated_data: schemas.OrderUpdate, 
    current_user: models.User
):
    db_Order = get_Order_by_id(db, Order_id)
    if not db_Order:
        return None

    # Получаем данные из схемы, но исключаем неустановленные поля
    update_data = updated_data.model_dump(exclude_unset=True)

    # Автоматически подставляем ФИО мастера
    master_full_name = f"{current_user.last_name} {current_user.first_name} {current_user.patronymic}"
    update_data["master"] = master_full_name

    # Применяем обновления к объекту БД
    for key, value in update_data.items():
        setattr(db_Order, key, value)

    db.commit()
    db.refresh(db_Order)
    return db_Order

def filter_orders(db: Session, *, status: Optional[str] = None, urgent: Optional[bool] = None, client: Optional[str] = None, master: Optional[str] = None):
    query = db.query(models.Order)

    if status is not None:
        query = query.filter(models.Order.status == status)
    if urgent is not None:
        query = query.filter(models.Order.urgent == urgent)
    if client is not None:
        query = query.filter(models.Order.client.ilike(f"%{client}%"))
    if master is not None:
        query = query.filter(models.Order.master.ilike(f"%{master}%"))

    return query.all()

def get_Orders_filtered(db: Session, status: str):
    return db.query(models.Order).filter(models.Order.status == status).all()

# Получить всех пользователей
def get_all_users(db: Session):
    return db.query(models.User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Обновить данные пользователя
def update_user(db: Session, user_id: int, updated_data: schemas.UserResponse):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

# Удалить пользователя
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
