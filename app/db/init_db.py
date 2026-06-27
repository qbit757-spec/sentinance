import structlog
from tenacity import retry, stop_after_attempt, wait_fixed
from app.db.session import engine
from app.db.base import Base

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(10),
    wait=wait_fixed(3),
    before_sleep=lambda retry_state: logger.warn(
        "db_connection_failed_retrying",
        attempt=retry_state.attempt_number,
    ),
)
async def try_connect_and_create():
    async with engine.begin() as conn:
        logger.info("connecting_to_database")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_created_successfully")


async def init_db():
    try:
        await try_connect_and_create()
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        raise e
