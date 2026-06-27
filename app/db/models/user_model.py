from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    debts = relationship("Debt", back_populates="user", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="creator", cascade="all, delete-orphan")
    shared_goals = relationship("GoalUser", back_populates="user", cascade="all, delete-orphan")
    sent_invitations = relationship(
        "GoalInvitation",
        foreign_keys="GoalInvitation.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_invitations = relationship(
        "GoalInvitation",
        foreign_keys="GoalInvitation.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
