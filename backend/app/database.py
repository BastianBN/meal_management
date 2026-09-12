from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def migrate_columns(sync_conn):
            from sqlalchemy import text
            try:
                res = sync_conn.execute(text("PRAGMA table_info(restaurants);")).fetchall()
                existing_cols = {row[1] for row in res}
                if existing_cols:
                    if "rating" not in existing_cols:
                        sync_conn.execute(text("ALTER TABLE restaurants ADD COLUMN rating FLOAT;"))
                    if "rating_count" not in existing_cols:
                        sync_conn.execute(text("ALTER TABLE restaurants ADD COLUMN rating_count INTEGER;"))
            except Exception:
                pass

        await conn.run_sync(migrate_columns)

