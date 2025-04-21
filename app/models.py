from pydantic import BaseModel
from datetime import datetime
from databases import Database


DATABASE_URL = "postgresql://dae22:1998@localhost/mydatabase"
database = Database(DATABASE_URL)


USER_ROLES = {"client", "moderator"}
CITIES = {"Москва", "Санкт-Петербург", "Казань"}


class UserCreate(BaseModel):
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PVZCreate(BaseModel):
    city: str

class ReceptionCreate(BaseModel):
    pickup_point_id: int

class ProductCreate(BaseModel):
    type: str


async  def create_user(user: UserCreate):
    query = "INSERT INTO users (email, password, role) VALUES (:email, :password, :role)"
    await database.execute(query, user.dict())
    return {"message": "Пользователь добавлен"}

async def login_user(user: UserLogin):
    query = "SELECT * FROM users WHERE email=:email AND password=:password"
    return await database.fetch_one(query=query, values=UserLogin.dict())

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

async def remove_last(pickup_point_id: int):
    query = "SELECT id FROM receptions WHERE pickup_point_id=:pickup_point_id and status='in_progress'"
    reception = await database.fetch_one(query=query, values={"pickup_point_id": pickup_point_id})
    if not reception:
        raise ValueError("Нет открытой приемки")
    query = "SELECT id FROM products WHERE reception_id=:reception_id ORDER BY id DESC LIMIT 1"
    product = await database.fetch_one(query=query, values={"reception_id": reception['id']})
    if not product:
        raise ValueError("Нет товаров для удаления")
    query = "DELETE FROM products WHERE id=:product_id"
    await database.execute(query=query, values={"product_id": product["id"]})

async def close_reception(pvz_id: int):
    query = "UPDATE receptions SET status = 'closed' WHERE pvz_id = :pvz_id AND status = 'in_progress'"
    await database.execute(query,{"pvz_id": pvz_id})
    return {"message": "Приемка закрыта"}

async def get_pp_and_receptions(start: datetime, end: datetime):
    query = """
    SELECT  FROM pickup_points as p
    JOIN receptions as r ON p.id = r.pickup_point_id
    WHERE r.date BETWEEN :start AND :end
    """
    return await database.fetch_all(query=query, values={"start": start, "end": end})
