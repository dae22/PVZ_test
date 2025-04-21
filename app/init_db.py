import asyncpg
import asyncio

DATABASE_URL = "postgresql://dae22:1998@localhost/mydatabase"

async def create_table_users():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(''' CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL
    )
''')
    await conn.close()

async def create_table_pickup():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(''' CREATE TABLE IF NOT EXISTS pickup_points (
    id UUID PRIMARY KEY,
    registration_date TIMESTAMP NOT NULL,
    city TEXT NOT NULL
    )
''')
    await conn.close()

async def create_table_receptions():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''CREATE TABLE IF NOT EXISTS receptions (
    id UUID PRIMARY KEY,
    date_time TIMESTAMP NOT NULL,
    pickup_point_id UUID REFERENCES pickup_points(id),
    status TEXT NOT NULL
    )
''')
    await conn.close()

async def create_table_products():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY,
    date_time TIMESTAMP NOT NULL,
    reception_id UUID REFERENCES receptions(id),
    product_type TEXT NOT NULL
    )
''')
    await conn.close()

asyncio.run(create_table_users())
asyncio.run(create_table_pickup())
asyncio.run(create_table_receptions())
asyncio.run(create_table_products())
