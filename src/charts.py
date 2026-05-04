import matplotlib.pyplot as plt
import logging
from asyncpg import Pool
from pathlib import Path
from datetime import datetime
from src.analytics import get_TopTA, get_category_breakdown

async def generate_category_chart(conn_pool: Pool, output_path: Path):
    rows = await get_category_breakdown(conn_pool)
    if not rows:
        logging.warning("No data to generate chart")
        return False
    
    name = [row["name"] for row in rows]
    amount = [row["amount"] for row in rows]
    
    # Generate graphs
    plt.figure()
    plt.bar(name, amount)
    plt.title("Transactions History")
    plt.xlabel("Category")
    plt.ylabel("Amount")

    plt.savefig(output_path / f"full_statistic_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png")
    plt.close()
    return True
    
async def generate_TopTransactions_chart(conn_pool: Pool, output_path: Path, top_n: int):
    rows = await get_TopTA(conn_pool, top_n)
    if not rows:
        logging.warning("No data to generate chart")
        return False
    
    name = [row["description"] for row in rows]
    amount = [row["amount"] for row in rows]
    
    # Generate graphs
    plt.figure()
    plt.bar(name, amount)
    plt.title("Top Transactions")
    plt.xlabel("Category")
    plt.ylabel("Amount")

    plt.savefig(output_path / f"top_statistic_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png")
    plt.close()
    return True
    
