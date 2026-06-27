import structlog

logger = structlog.get_logger()


async def log_financial_transaction_activity(user_id: int, transaction_type: str, amount: float):
    """
    Loggea actividades financieras críticas en segundo plano para auditoría.
    """
    logger.info(
        "financial_transaction_logged_background",
        user_id=user_id,
        transaction_type=transaction_type,
        amount=amount
    )
