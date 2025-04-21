from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models import *


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/dummyLogin")


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/dummyLogin")
async def dummy_login(dummy: Dummy):
    return {"access_token": f"dummy_{dummy.role}_token"}

@app.post("/register")
async def registration(user: UserCreate):
    await create_user(user)
    return {"message": "Пользователь зарегистрирован"}

@app.post("/login")
async def login(user: UserLogin):
    db_user = await login_user(user)
    if not db_user:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    return {"access_token": f"dummy_{db_user['role']}_token"}

@app.post("/pickup_points")
async def create_pickup_point(pvz: PVZCreate, token: str = Depends(oauth2_scheme)):
    if token != "dummy_moderator_token":
        raise HTTPException(status_code=403, detail="Только модераторы могут создавать ПВЗ")
    pickup_point_id = await create_pickup_point(pvz.city)
    return {"pickup_point_id": pickup_point_id, "city": pvz.city}

@app.post("/receptions")
async def create_receptions(reception: ReceptionCreate, token: str = Depends(oauth2_scheme)):
    if token != "dummy_staff_token":
        raise HTTPException(status_code=403, detail="Только сотрудники могут создавать приемки")
    try:
        reception_id = await create_reception(reception.pickup_point_id)
        return {"id": reception_id, "status": "in progress"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/products")
async def add_products(pickup_point_id: int, product: ProductCreate, token: str = Depends(oauth2_scheme)):
    if token != "dummy_staff_token":
        raise HTTPException(status_code=403, detail="Только сотрудники могут добавлять товары")
    try:
        product_id = await add_product(pickup_point_id, product.type)
        return {"id": product_id, "type": product.type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/products/last")
async def remove_last_product(pickup_point_id: int, token: str = Depends(oauth2_scheme)):
    if token != "dummy_staff_token":
        raise HTTPException(status_code=403, detail="Только сотрудники могут удалять товары")
    try:
        await remove_last(pickup_point_id)
        return {"message": "Товар удален"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/receptions/close")
async def close_reception(pickup_point_id: int, token: str = Depends(oauth2_scheme)):
    if token != "dummy_staff_token":
        raise HTTPException(status_code=403, detail="Только сотрудники могут закрывать приемки")
    try:
        await close_reception(pickup_point_id)
        return {"message": "Приемка закрыта"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/pickup_points")
async def get_pickup_points(start: datetime, end: datetime, token: str = Depends(oauth2_scheme)):
    if token not in ["dummy_staff_token", "dummy_moderator_token"]:
        raise HTTPException(status_code=403, detail="Только сотрудники и модераторы могут просматривать ПВЗ")
    return await get_pp_and_receptions(start, end)