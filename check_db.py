import asyncio
from sqlalchemy import select, func
from shared.database import AsyncSessionLocal
from shared.models.articles import Article

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Article.status, func.count()).group_by(Article.status)
        )
        counts = result.all()
        print("Article Counts by Status:")
        for status, count in counts:
            print(f"- {status.value}: {count}")

if __name__ == "__main__":
    asyncio.run(main())
