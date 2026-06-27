from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.schemas.account_schema import AccountCreate, AccountUpdate, AccountResponse
from app.services.finance_service import FinanceService
from app.repositories.account_repo import AccountRepository

router = APIRouter()


@router.get("", response_model=list[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    account_repo = AccountRepository(db)
    finance_service = FinanceService(db)
    accounts = await account_repo.get_by_user(current_user.id)
    
    response = []
    for acc in accounts:
        real_bal = await finance_service.get_real_balance(acc.id, current_user.id)
        proj_bal = await finance_service.get_projected_balance(acc.id, current_user.id)
        
        acc_resp = AccountResponse.model_validate(acc)
        acc_resp.real_balance = real_bal
        acc_resp.projected_balance = proj_bal
        response.append(acc_resp)
        
    return response


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_in: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    acc = await finance_service.create_account(current_user.id, account_in.model_dump())
    
    real_bal = await finance_service.get_real_balance(acc.id, current_user.id)
    proj_bal = await finance_service.get_projected_balance(acc.id, current_user.id)
    
    acc_resp = AccountResponse.model_validate(acc)
    acc_resp.real_balance = real_bal
    acc_resp.projected_balance = proj_bal
    return acc_resp


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account_repo = AccountRepository(db)
    acc = await account_repo.get_by_user_and_id(current_user.id, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        
    finance_service = FinanceService(db)
    real_bal = await finance_service.get_real_balance(acc.id, current_user.id)
    proj_bal = await finance_service.get_projected_balance(acc.id, current_user.id)
    
    acc_resp = AccountResponse.model_validate(acc)
    acc_resp.real_balance = real_bal
    acc_resp.projected_balance = proj_bal
    return acc_resp


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_in: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account_repo = AccountRepository(db)
    acc = await account_repo.get_by_user_and_id(current_user.id, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        
    updated_acc = await account_repo.update(acc, account_in.model_dump(exclude_unset=True))
    await db.commit()
    
    finance_service = FinanceService(db)
    real_bal = await finance_service.get_real_balance(updated_acc.id, current_user.id)
    proj_bal = await finance_service.get_projected_balance(updated_acc.id, current_user.id)
    
    acc_resp = AccountResponse.model_validate(updated_acc)
    acc_resp.real_balance = real_bal
    acc_resp.projected_balance = proj_bal
    return acc_resp


@router.delete("/{account_id}", response_model=AccountResponse)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account_repo = AccountRepository(db)
    acc = await account_repo.get_by_user_and_id(current_user.id, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        
    deleted_acc = await account_repo.remove(account_id)
    await db.commit()
    
    finance_service = FinanceService(db)
    acc_resp = AccountResponse.model_validate(deleted_acc)
    acc_resp.real_balance = Decimal("0.00")
    acc_resp.projected_balance = Decimal("0.00")
    return acc_resp
