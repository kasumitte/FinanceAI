from openai import AsyncOpenAI
from src.config import Conf
from src.cli import App
from src.database import init_db
import asyncio
import asyncpg

async def main():
    config = Conf.load_config()
    pool = await asyncpg.create_pool(
        dsn=config.database_url
    )
    client = AsyncOpenAI(api_key=config.llm_api_key, base_url="https://api.groq.com/openai/v1")
    
    await init_db(pool)
    app = App(pool=pool, client=client, outpath=config.graph_path)
    await app.run()
    
def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()