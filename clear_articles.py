import asyncio
from sqlalchemy import text
from shared.database import AsyncSessionLocal

async def clear_db():
    async with AsyncSessionLocal() as db:
        print("Clearing all old articles and collection history...")
        await db.execute(text("TRUNCATE TABLE articles CASCADE;"))
        await db.execute(text("TRUNCATE TABLE collection_runs CASCADE;"))
        await db.commit()
        print("Success! The database is completely clean.")

if __name__ == "__main__":
    asyncio.run(clear_db())
