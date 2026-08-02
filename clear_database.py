import asyncio
import sys
from pathlib import Path

# Add the root directory to the python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from shared.database import AsyncSessionLocal, Base
# Import all models so they are registered with Base.metadata
from shared.models import *

async def clear_database():
    print("WARNING: This will delete ALL data from the database!")
    confirm = input("Are you sure you want to proceed? Type 'yes' to confirm: ")
    
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return

    async with AsyncSessionLocal() as db:
        # Get all table names registered in SQLAlchemy models
        tables = list(Base.metadata.tables.keys())
        
        if not tables:
            print("No tables found in metadata.")
            return
            
        print(f"Found {len(tables)} tables to clear...")
        
        # TRUNCATE ALL tables with CASCADE to handle foreign key dependencies
        table_names = ", ".join(tables)
        query = f"TRUNCATE {table_names} CASCADE;"
        
        try:
            print("Executing TRUNCATE CASCADE...")
            await db.execute(text(query))
            await db.commit()
            print("Successfully cleared all data from the database!")
        except Exception as e:
            await db.rollback()
            print(f"Failed to clear database: {e}")

if __name__ == '__main__':
    asyncio.run(clear_database())
