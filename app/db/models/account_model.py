from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # ej: Ahorros, Corriente, Efectivo, Tarjeta de Crédito
    currency = Column(String(10), nullable=False)  # Soles / Dólares
    base_balance = Column(Numeric(12, 2), default=0.00, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="accounts")
    incomes = relationship("Income", back_populates="account")
    expenses = relationship("Expense", back_populates="account")
    debts = relationship("Debt", back_populates="account")
    loans = relationship("Loan", back_populates="account")
