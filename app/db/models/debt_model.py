from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    creditor = Column(String(100), nullable=False)
    original_amount = Column(Numeric(12, 2), nullable=False)
    pending_balance = Column(Numeric(12, 2), nullable=False)
    type = Column(String(50), nullable=False)  # Directa o En Cuotas
    total_installments = Column(Integer, default=0, nullable=False)
    paid_installments = Column(Integer, default=0, nullable=False)
    interest_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    amortizes_capital = Column(Boolean, default=False, nullable=False)
    next_due_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="debts")
    account = relationship("Account", back_populates="debts")
    payments = relationship("DebtPayment", back_populates="debt", cascade="all, delete-orphan")


class DebtPayment(Base):
    __tablename__ = "debt_payments"

    id = Column(Integer, primary_key=True, index=True)
    debt_id = Column(Integer, ForeignKey("debts.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    is_capital_amortization = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    debt = relationship("Debt", back_populates="payments")
