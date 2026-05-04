import asyncpg
import logging
from datetime import datetime, date

async def init_db(conn_pool: asyncpg.Pool):
    async with conn_pool.acquire() as conn:
        await conn.execute(""" CREATE TABLE IF NOT EXISTS category (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE
                )""")
        
        await conn.execute(""" CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    date DATE,
                    description TEXT,
                    amount DECIMAL,
                    category_id INTEGER REFERENCES category(id),
                    created_at TIMESTAMP
                )""")


async def get_transactions_w_category(conn_pool: asyncpg.Pool):
    """ All transactions with category for analytics and list commands """
    async with conn_pool.acquire() as conn:
        return await conn.fetch(""" SELECT transactions.description, transactions.amount, category.name 
                           FROM transactions
                           JOIN category ON transactions.category_id = category.id """)      
        
async def save_transaction(conn_pool: asyncpg.Pool, description: str, amount: float, date: date):
    try:
        async with conn_pool.acquire() as conn:
            await conn.execute(""" INSERT INTO transactions (description, amount, created_at, date)
                                VALUES ($1, $2, $3, $4) """, description, amount, datetime.now(), date)
        return True
    except asyncpg.PostgresError:
        logging.error("Database Error")
        return False
    
async def get_RawTransactions(conn_pool: asyncpg.Pool):
    async with conn_pool.acquire() as conn:
        return await conn.fetch(""" SELECT * FROM transactions ORDER BY created_at DESC """)
    
async def update_TransactionCategory(conn_pool: asyncpg.Pool, cat_name: str, cat_id: int):
    async with conn_pool.acquire() as conn:
        await conn.execute(""" UPDATE transactions SET category_id = (
                                SELECT id FROM category WHERE name = $1
                            ) WHERE id = $2 """, cat_name, cat_id)
        
async def add_category(conn_pool: asyncpg.Pool, cat_name: str):
    async with conn_pool.acquire() as conn:
        await conn.execute(""" INSERT INTO category (name) VALUES ($1)""", cat_name)

        
async def get_transactions_withoutCat(conn_pool: asyncpg.Pool):
    """ Get transactions without category for AI categorizer """
    async with conn_pool.acquire() as conn:
        return await conn.fetch(""" SELECT * FROM transactions WHERE category_id IS NULL """)
        
        
async def getTransactions_specMonth(conn_pool: asyncpg.Pool, act_month: str):
    async with conn_pool.acquire() as conn:
        return await conn.fetch(""" SELECT * FROM transactions 
                                WHERE EXTRACT(YEAR FROM date) = $1
                                AND EXTRACT(MONTH FROM date) = $2 """, act_month.split("-")[0], act_month.split("-")[1])

async def get_TopTransactions(conn_pool: asyncpg.Pool, top_n: int):
    async with conn_pool.acquire() as conn:
        return await conn.fetch(""" SELECT * FROM transactions ORDER BY amount DESC LIMIT $1 """, top_n)   
    
async def get_category_summary(conn_pool: asyncpg.Pool):
    async with conn_pool.acquire() as conn:
        return await conn.fetch(""" SELECT category.name, SUM(transactions.amount) FROM transactions
                                JOIN category ON transactions.category_id = category.id
                                GROUP BY category.name """)

