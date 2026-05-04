from asyncpg import Pool
from src.database import get_TopTransactions, getTransactions_specMonth, get_category_summary


async def get_monthly_stats(conn_pool: Pool, month: str):
    """ 
    Returns total amount from 'getTransactions_specMonth' function in db for given month (YYYY-MM format).
    Returns None if no transactions found.
    """
    stats = await getTransactions_specMonth(conn_pool, month)
    if not stats:
        return None
    return sum(row["amount"] for row in stats)

async def get_category_breakdown(conn_pool: Pool):
    """ Returns already counted amount sorted by category. """
    cat_sum = await get_category_summary(conn_pool)
    return cat_sum
     
async def get_TopTA(conn_pool: Pool, top_n: int):
    """ Returns top transactions. """
    top_t = await get_TopTransactions(conn_pool, top_n)
    return top_t
