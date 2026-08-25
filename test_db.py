import asyncio
from shared.database import engine

async def test():
    try:
        async with engine.connect() as conn:
            print("Connected successfully!")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test())
