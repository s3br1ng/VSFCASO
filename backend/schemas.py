from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

#Модель для создания заявки
class OrderBase(BaseModel):
    id : Optional [int] = None
    name: str
    urgent : bool
    description : str
    status : str
    client: Optional[str] = None
    master: Optional[str] = None

#Модель для обновления данных заявки
class OrderUpdate(BaseModel):
    name: Optional[str] = None
    urgent: Optional[bool] = None
    description: Optional[str] = None
    status: Optional[str] = None
    client: Optional[str] = None
    master : Optional[str] = None 
    

#Модель для входа пользователя
class UserLogin(BaseModel):
    nickname: str
    password: str

class Register(BaseModel):
    nickname: str
    password: str = Field(min_length=6)
    role: str
    last_name: str
    first_name: str
    patronymic: str
    date_of_birth: date
    department: str
    position: str
    

class UserResponse(BaseModel):
    nickname: str
    role: str
    last_name: str
    first_name: str
    patronymic: str
    date_of_birth: date
    department: str
    position: str
    id: Optional[int] = None

#Модель для получения токена и его типа
class Token(BaseModel):
    access_token: str
    token_type: str

#Модель для получения информации о профиле
class UserProfile(BaseModel):
    id: int
    nickname: str
    role : str
    last_name : str
    first_name : str
    patronymic : str
    date_of_birth : date
    department : str
    position : str
