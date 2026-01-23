import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings
from db_base import Base

logger = logging.getLogger(__name__)

# Create async engine with increased timeout for Render
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "timeout": 30,
        "command_timeout": 30,
    } if "asyncpg" in settings.database_url else {},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Dependency for FastAPI route handlers to get async session"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db(max_retries: int = 15, base_delay: float = 2.0):
    """Initialize database: create all tables with retry logic

    Args:
        max_retries: Maximum number of connection attempts (increased for Render)
        base_delay: Base delay in seconds (exponential backoff)
    """
    retry_count = 0
    delay = base_delay

    while retry_count < max_retries:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
            return
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Database initialization failed after {max_retries} attempts: {e}")
                raise

            # Exponential backoff with jitter
            current_delay = delay * (2 ** (retry_count - 1)) + (retry_count * 0.1)
            logger.warning(
                f"Database connection attempt {retry_count}/{max_retries} failed: {e}. "
                f"Retrying in {current_delay:.1f}s..."
            )
            await asyncio.sleep(current_delay)


async def close_db():
    """Close database connection pool"""
    await engine.dispose()


# Import database models after Base is defined (registering them with metadata)
from db_models import Identity, Credential, AccessGrant, Verification  # noqa: E402, F401
