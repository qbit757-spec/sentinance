from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models for SQLAlchemy metadata registration
from app.db.models.user_model import User
from app.db.models.account_model import Account
from app.db.models.category_model import Category
from app.db.models.income_model import Income
from app.db.models.expense_model import Expense
from app.db.models.debt_model import Debt, DebtPayment
from app.db.models.loan_model import Loan
from app.db.models.goal_model import Goal, GoalUser, GoalInvitation

