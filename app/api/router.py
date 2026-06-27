from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    accounts,
    categories,
    incomes,
    expenses,
    debts,
    loans,
    goals,
    dashboard,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(incomes.router, prefix="/incomes", tags=["incomes"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(debts.router, prefix="/debts", tags=["debts"])
api_router.include_router(loans.router, prefix="/loans", tags=["loans"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
