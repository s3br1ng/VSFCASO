# backend/.venv/Scripts/Activate.ps1
# uvicorn backend.main:app --reload


from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import crud, models, schemas, auth, database
from datetime import datetime
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Создает новую сессию базы данных, для работы запросов с дб, потом закрывает
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
async def get_current_user(
    token: dict = Depends(auth.decode_access_token),
    db: Session = Depends(get_db)):
    nickname = token.get("sub")
    user = crud.get_user_by_nickname(db, nickname)
    return user

#Регистрация аккаунта, проверка ника на уникальность
@app.post("/register")
def register_user(user: schemas.Register, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_nickname(db, user.nickname)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname already registered")
    created_user = crud.create_user(db=db, user=user)
    return created_user

#Вход пользователя, ник проверяется на уникальность, при входе сохраняет актуальный токен, возвращает токен и его тип
@app.post("/login", response_model=schemas.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.nickname, user.password)
    access_token = auth.create_access_token({"sub": db_user.nickname})
    return {"access_token": access_token, "token_type": "bearer"}

# Создание заявки при помощи токена
@app.post("/Orders/", response_model=schemas.OrderBase)
def create_Order(
    Order: schemas.OrderBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_Order(db=db, Order=Order, current_user=current_user)

@app.get("/Orders/filter", response_model=List[schemas.OrderBase])
def filter_orders(
    status: Optional[str] = None,
    urgent: Optional[bool] = None,
    client: Optional[str] = None,
    master: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.filter_orders(db, status=status, urgent=urgent, client=client, master=master)

#Вывод всех заявок, имеющихся в бд
@app.get("/Orders/", response_model=List[schemas.OrderBase])
def read_Orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_Orders(db)
 
#Обновление заявки, проверяет ее наличие, проверяет токен на корректность
@app.post("/Orders/{Order_id}/update", response_model=schemas.OrderUpdate)
def update_Order(
    Order_id: int,
    updated_data: schemas.OrderUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["technic", "admin"]:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    updated_Order = crud.update_Order(db=db, Order_id=Order_id, updated_data=updated_data, current_user=current_user)
    
    if not updated_Order:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
        
    return updated_Order

#Вывод информации о профиле
@app.get("/profile", response_model=schemas.UserProfile)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

# Добавьте новый GET-эндпоинт для получения заявки по ID
@app.get("/Orders/{Order_id}", response_model=schemas.OrderBase)
def read_Order(Order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_Order = crud.get_Order_by_id(db, Order_id)
    if not db_Order:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return db_Order

# Получить пользователя по ID (только для админа)
@app.get("/admin/users/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

# Обновить данные пользователя (только для админа)
@app.post("/admin/users/{user_id}/update", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    updated_data: schemas.UserResponse,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.update_user(db, user_id, updated_data)

# Удалить пользователя (только для админа)
@app.delete("/admin/users/{user_id}/delete", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Нельзя удалить себя")
    crud.delete_user(db, user_id)
    return {"detail": "Пользователь удален"}

# Получить список всех пользователей (только для админа)
@app.get("/admin/users", response_model=List[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.get_all_users(db)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory="static", html=True), name="html")
app.mount("/assets", StaticFiles(directory="static"), name="static")




