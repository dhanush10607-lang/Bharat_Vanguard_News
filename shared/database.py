"""
Bharat Vanguard News (BVN) — Database Connection
Async SQLAlchemy engine + session factory for Supabase PostgreSQL.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from shared.config import settings


# Async engine (used by the API server)
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,         # Reconnect on stale connections
    pool_recycle=3600,          # Recycle connections every hour
    connect_args={"timeout": 60, "command_timeout": 60}, # Give cloud DB time to wake up
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides a database session.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Only used in development; production uses Alembic."""
    async with engine.begin() as conn:
        import shared.models  # noqa: F401 — import all models so Base knows about them
        await conn.run_sync(Base.metadata.create_all)
