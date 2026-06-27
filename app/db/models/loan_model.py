from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    debtor = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    date_granted = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="Pendiente", nullable=False)  # Pendiente o Cobrado
    is_installment_loan = Column(Boolean, default=False, nullable=False)
    interest_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    total_installments = Column(Integer, default=0, nullable=False)
    installments_paid = Column(Integer, default=0, nullable=False)
    payment_day = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="loans")
    account = relationship("Account", back_populates="loans")
