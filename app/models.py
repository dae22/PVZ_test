from pydantic import BaseModel
from datetime import datetime
from databases import Database


DATABASE_URL = "postgresql://dae22:1998@localhost/mydatabase"
database = Database(DATABASE_URL)


USER_ROLES = {"client", "moderator"}
CITIES = {"Москва", "Санкт-Петербург", "Казань"}


class Token(BaseModel):
    access_token: str
    token_type: str

class PVZCreate(BaseModel):
    city: str

class ReceptionCreate(BaseModel):
    pvz_id: int

class ProductCreate(BaseModel):
    type: str


async  def create_user():
    pass


async def create_pickup_point(city: str):
    if city not in CITIES:
        raise ValueError("Город не поддерживается")
    query = "INSERT INTO pickup_points (city) VALUES (:city) RETURNING id"
    return await database.execute(query, {"city": city})


async def create_reception(pickup_point_id: int):
    query = "SELECT id FROM receptions WHERE pickup_point_id = :pickup_point_id AND status = 'in_progress'"
    open_reception = await database.fetch_one(query,{"pickup_point_id": pickup_point_id})
    if open_reception:
        raise ValueError("Уже есть открытая приемка")
    query = "INSERT INTO receptions (pickup_point_id, status) VALUES (:pickup_point_id, 'in_progress')"
    await database.execute(query,{"pickup_point_id": pickup_point_id})
    return {"message": "Приемка добавлена"}

async def add_product(pickup_point_id: int, product_type: str):
    query = "SELECT id FROM receptions WHERE pickup_point_id = :pickup_point_id AND status = 'in_progress'"
    reception = await database.fetch_one(query,{"pickup_point_id": pickup_point_id})
    if not reception:
        raise ValueError("Нет открытой приемки")
    query = "INSERT INTO products (reception_id, date, type) VALUES (:reception_id, now(), :type) RETURNING id"
    await database.execute(query,{"reception_id": reception["id"], "type": product_type})
    return {"message": "Товар добавлен"}

async def close_reception(pvz_id: int):
    query = "UPDATE receptions SET status = 'closed' WHERE pvz_id = :pvz_id AND status = 'in_progress'"
    await database.execute(query,{"pvz_id": pvz_id})
    return {"message": "Приемка закрыта"}