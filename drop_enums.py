import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from shared.database import engine

async def drop_enums():
    # PostgreSQL ENUM types left behind by Alembic downgrade
    enum_types = [
        "entitytype",
        "articlestatus",
        "sentimentlabel",
        "userrole",
        "eventsentiment"
    ]
    
    async with engine.begin() as conn:
        for enum in enum_types:
            print(f"Dropping enum type: {enum}")
            await conn.execute(text(f"DROP TYPE IF EXISTS {enum} CASCADE;"))
            
    print("All ENUM types dropped successfully.")

if __name__ == "__main__":
    asyncio.run(drop_enums())
