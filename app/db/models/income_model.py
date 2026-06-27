from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), nullable=False)  # Liquidado o Por liquidar
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="incomes")
    account = relationship("Account", back_populates="incomes")
    category = relationship("Category", back_populates="incomes")
    goal = relationship("Goal", back_populates="incomes")
