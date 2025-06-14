from jose import jwt
from datetime import datetime, timedelta
from .schemas import Token
from passlib.context import CryptContext
from fastapi import Query
from typing import Optional


SECRET_KEY = "zyabliki"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#Принимает данные пользователя, затем защифровывает их в jwt токен, указывая его время дейтсвие
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#Функция для расшифровки токена. Принимает токен через URL при помощи query параметра
def decode_access_token(token = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None
    
