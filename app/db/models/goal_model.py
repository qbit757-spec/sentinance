from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    target_date = Column(DateTime, nullable=False)
    accumulated_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    priority = Column(String(50), default="Media", nullable=False)  # Baja, Media, Alta
    status = Column(String(50), default="En progreso", nullable=False)  # En progreso, Completada
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    creator = relationship("User", back_populates="goals")
    shared_users = relationship("GoalUser", back_populates="goal", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="goal")
    invitations = relationship("GoalInvitation", back_populates="goal", cascade="all, delete-orphan")


class GoalUser(Base):
    __tablename__ = "goal_users"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    goal = relationship("Goal", back_populates="shared_users")
    user = relationship("User", back_populates="shared_goals")


class GoalInvitation(Base):
    __tablename__ = "goal_invitations"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="Pendiente", nullable=False)  # Pendiente, Aceptada, Rechazada
    sent_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    goal = relationship("Goal", back_populates="invitations")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_invitations")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_invitations")
