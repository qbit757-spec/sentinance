from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_, extract, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.account_model import Account
from app.db.models.category_model import Category
from app.db.models.income_model import Income
from app.db.models.expense_model import Expense
from app.db.models.debt_model import Debt, DebtPayment
from app.db.models.loan_model import Loan
from app.db.models.goal_model import Goal, GoalUser, GoalInvitation
from app.repositories.account_repo import AccountRepository
from app.repositories.category_repo import CategoryRepository
from app.repositories.income_repo import IncomeRepository
from app.repositories.expense_repo import ExpenseRepository
from app.repositories.debt_repo import DebtRepository
from app.repositories.loan_repo import LoanRepository
from app.repositories.goal_repo import GoalRepository
from app.repositories.user_repo import UserRepository


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.category_repo = CategoryRepository(db)
        self.income_repo = IncomeRepository(db)
        self.expense_repo = ExpenseRepository(db)
        self.debt_repo = DebtRepository(db)
        self.loan_repo = LoanRepository(db)
        self.goal_repo = GoalRepository(db)
        self.user_repo = UserRepository(db)

    # --- Calculations ---
    async def get_real_balance(self, account_id: int, user_id: int, up_to_date: datetime | None = None) -> Decimal:
        account = await self.account_repo.get_by_user_and_id(user_id, account_id)
        if not account:
            return Decimal("0.00")

        limit_date = up_to_date or datetime.utcnow()
        # actual limit definition
        today = datetime.utcnow().date()
        if limit_date.date() < today:
            actual_limit = datetime.combine(limit_date.date(), datetime.max.time())
        else:
            actual_limit = datetime.combine(today, datetime.max.time())

        # Sum of cleared incomes
        cleared_incomes_res = await self.db.execute(
            select(func.coalesce(func.sum(Income.amount), 0)).where(
                Income.account_id == account_id,
                Income.date <= actual_limit,
                Income.is_active == True
            )
        )
        cleared_incomes = Decimal(str(cleared_incomes_res.scalar() or 0.00))

        # Sum of paid expenses
        paid_expenses_res = await self.db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.account_id == account_id,
                Expense.date <= actual_limit,
                Expense.is_active == True
            )
        )
        paid_expenses = Decimal(str(paid_expenses_res.scalar() or 0.00))

        # Sum of paid debt quotas
        paid_debt_quotas_res = await self.db.execute(
            select(func.coalesce(func.sum(DebtPayment.amount), 0))
            .join(Debt)
            .where(
                Debt.account_id == account_id,
                DebtPayment.date <= actual_limit,
                DebtPayment.is_active == True
            )
        )
        paid_debt_quotas = Decimal(str(paid_debt_quotas_res.scalar() or 0.00))

        return account.base_balance + cleared_incomes - paid_expenses - paid_debt_quotas

    async def get_projected_balance(self, account_id: int, user_id: int) -> Decimal:
        real_balance = await self.get_real_balance(account_id, user_id)
        end_of_today = datetime.combine(datetime.utcnow().date(), datetime.max.time())

        # Pending incomes
        pending_incomes_res = await self.db.execute(
            select(func.coalesce(func.sum(Income.amount), 0)).where(
                Income.account_id == account_id,
                Income.date > end_of_today,
                Income.is_active == True
            )
        )
        pending_incomes = Decimal(str(pending_incomes_res.scalar() or 0.00))

        # Pending expenses
        pending_expenses_res = await self.db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.account_id == account_id,
                Expense.date > end_of_today,
                Expense.is_active == True
            )
        )
        pending_expenses = Decimal(str(pending_expenses_res.scalar() or 0.00))

        return real_balance + pending_incomes - pending_expenses

    async def get_net_worth(self, user_id: int, up_to_date: datetime | None = None) -> Decimal:
        accounts = await self.account_repo.get_by_user(user_id)
        total_accounts_balance = Decimal("0.00")
        for acc in accounts:
            total_accounts_balance += await self.get_real_balance(acc.id, user_id, up_to_date)

        # Pending debts
        pending_debts_res = await self.db.execute(
            select(func.coalesce(func.sum(Debt.pending_balance), 0)).where(
                Debt.user_id == user_id,
                Debt.is_active == True
            )
        )
        pending_debts = Decimal(str(pending_debts_res.scalar() or 0.00))

        return total_accounts_balance - pending_debts

    # --- Core Account / Category CRUDs ---
    async def create_account(self, user_id: int, account_in: dict) -> Account:
        account_in["user_id"] = user_id
        account = await self.account_repo.create(account_in)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def create_category(self, user_id: int, category_in: dict) -> Category:
        category_in["user_id"] = user_id
        category = await self.category_repo.create(category_in)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    # --- Transactions & Automated Triggers ---
    async def create_income(self, user_id: int, income_in: dict) -> Income:
        income_in["user_id"] = user_id
        # Set status based on date
        today = datetime.utcnow().date()
        date_val = income_in.get("date")
        if isinstance(date_val, str):
            date_val = datetime.fromisoformat(date_val)
        
        if date_val.date() <= today:
            income_in["status"] = "Liquidado"
        else:
            income_in["status"] = "Por liquidar"

        income = await self.income_repo.create(income_in)

        # Abono a meta
        goal_id = income_in.get("goal_id")
        if goal_id:
            goal = await self.goal_repo.get_by_user_and_id(user_id, goal_id)
            if goal:
                goal.accumulated_amount += Decimal(str(income_in["amount"]))
                self.db.add(goal)

        await self.db.commit()
        await self.db.refresh(income)
        return income

    async def create_expense(self, user_id: int, expense_in: dict) -> Expense:
        expense_in["user_id"] = user_id
        today = datetime.utcnow().date()
        date_val = expense_in.get("date")
        if isinstance(date_val, str):
            date_val = datetime.fromisoformat(date_val)

        if date_val.date() <= today:
            expense_in["status"] = "Pagado"
        else:
            expense_in["status"] = "Por pagar"

        expense = await self.expense_repo.create(expense_in)
        await self.db.commit()
        await self.db.refresh(expense)
        return expense

    # --- Debts & Quotas ---
    async def create_debt(self, user_id: int, debt_in: dict) -> Debt:
        debt_in["user_id"] = user_id
        debt = await self.debt_repo.create(debt_in)
        await self.db.commit()
        await self.db.refresh(debt)
        return debt

    async def pay_debt_installment(
        self, user_id: int, debt_id: int, amount: Decimal, is_capital_amortization: bool
    ) -> DebtPayment:
        debt = await self.debt_repo.get_by_user_and_id(user_id, debt_id)
        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deuda no encontrada",
            )

        # Update debt properties
        debt.pending_balance = max(Decimal("0.00"), debt.pending_balance - amount)
        if not is_capital_amortization:
            debt.paid_installments += 1
            if debt.next_due_date:
                # Add 1 month approx
                # Simple logic: increment month
                next_m = debt.next_due_date.month + 1
                next_y = debt.next_due_date.year
                if next_m > 12:
                    next_m = 1
                    next_y += 1
                try:
                    debt.next_due_date = debt.next_due_date.replace(year=next_y, month=next_m)
                except ValueError:
                    # handle month end variations (e.g. 31 Jan -> 30 Feb)
                    debt.next_due_date = debt.next_due_date.replace(year=next_y, month=next_m, day=28)
        self.db.add(debt)

        # Create payment record
        payment_in = {
            "debt_id": debt_id,
            "amount": amount,
            "is_capital_amortization": is_capital_amortization,
            "date": datetime.utcnow()
        }
        payment = await self.debt_repo.create_payment(payment_in)

        # Auto create Expense to reduce account balance
        cat = await self.category_repo.get_by_name_and_type(user_id, "Pago de Deuda", "Gasto")
        if not cat:
            cat = await self.create_category(user_id, {"name": "Pago de Deuda", "type": "Gasto"})

        expense_in = {
            "account_id": debt.account_id,
            "category_id": cat.id,
            "description": f"Pago cuota: {debt.name}",
            "amount": amount,
            "date": datetime.utcnow(),
            "status": "Pagado"
        }
        await self.create_expense(user_id, expense_in)

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    # --- Loans ---
    async def create_loan(self, user_id: int, loan_in: dict) -> Loan:
        loan_in["user_id"] = user_id
        loan = await self.loan_repo.create(loan_in)

        # Auto create Expense to subtract from account
        account_id = loan_in.get("account_id")
        if account_id:
            cat = await self.category_repo.get_by_name_and_type(user_id, "Préstamos", "Gasto")
            if not cat:
                cat = await self.create_category(user_id, {"name": "Préstamos", "type": "Gasto"})

            expense_in = {
                "account_id": account_id,
                "category_id": cat.id,
                "description": f"Préstamo otorgado: {loan.description or ''}",
                "amount": loan.amount,
                "date": loan.date_granted,
                "status": "Pagado"
            }
            await self.create_expense(user_id, expense_in)

        await self.db.commit()
        await self.db.refresh(loan)
        return loan

    async def pay_loan(self, user_id: int, loan_id: int, full_pay: bool = False) -> Loan:
        loan = await self.loan_repo.get_by_user_and_id(user_id, loan_id)
        if not loan or loan.status == "Cobrado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Préstamo no encontrado o ya cobrado",
            )

        amount_to_pay = loan.amount
        if loan.is_installment_loan and not full_pay:
            # Installment payment logic
            amount_to_pay = (loan.amount + (loan.amount * (loan.interest_rate / 100))) / loan.total_installments
            loan.installments_paid += 1
            if loan.installments_paid >= loan.total_installments:
                loan.status = "Cobrado"
        else:
            if loan.is_installment_loan:
                # Full remaining payment with interest logic
                total_with_interest = loan.amount + (loan.amount * (loan.interest_rate / 100))
                installment_value = total_with_interest / loan.total_installments
                amount_to_pay = total_with_interest - (installment_value * loan.installments_paid)
                loan.installments_paid = loan.total_installments
            loan.status = "Cobrado"
        self.db.add(loan)

        # Auto create Income to add to account balance
        account_id_to_use = loan.account_id
        if not account_id_to_use:
            # fallback to first active user account
            user_accounts = await self.account_repo.get_by_user(user_id)
            if user_accounts:
                account_id_to_use = user_accounts[0].id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario no tiene una cuenta asociada para recibir el cobro",
                )

        cat = await self.category_repo.get_by_name_and_type(user_id, "Cobro de Préstamos", "Ingreso")
        if not cat:
            cat = await self.create_category(user_id, {"name": "Cobro de Préstamos", "type": "Ingreso"})

        desc = (
            f"Cobro de cuota {loan.installments_paid}/{loan.total_installments} de préstamo: {loan.description or ''}"
            if loan.is_installment_loan and not full_pay
            else f"Cobro de préstamo: {loan.description or ''}"
        )

        income_in = {
            "account_id": account_id_to_use,
            "category_id": cat.id,
            "description": desc,
            "amount": amount_to_pay,
            "date": datetime.utcnow(),
            "status": "Liquidado"
        }
        await self.create_income(user_id, income_in)

        await self.db.commit()
        await self.db.refresh(loan)
        return loan

    # --- Goals & Invitations ---
    async def create_goal(self, user_id: int, goal_in: dict) -> Goal:
        goal_in["user_id"] = user_id
        goal = await self.goal_repo.create(goal_in)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def send_goal_invitation(self, user_id: int, goal_id: int, receiver_username: str) -> GoalInvitation:
        goal = await self.goal_repo.get_by_user_and_id(user_id, goal_id)
        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta no encontrada o no tienes permisos de creador",
            )

        receiver = await self.user_repo.get_by_username(receiver_username)
        if not receiver or receiver.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no válido para invitar",
            )

        # Check collaborator
        is_collab = await self.goal_repo.check_collaborator_exists(goal_id, receiver.id)
        if is_collab:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya es colaborador en esta meta",
            )

        # Check existing invitation
        exists = await self.goal_repo.check_invitation_exists(goal_id, receiver.id)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una invitación pendiente para este usuario",
            )

        inv = await self.goal_repo.create_invitation(goal_id, user_id, receiver.id)
        await self.db.commit()
        await self.db.refresh(inv)
        return inv

    async def respond_to_invitation(self, user_id: int, invitation_id: int, accept: bool) -> GoalInvitation:
        inv = await self.goal_repo.get_invitation(invitation_id)
        if not inv or inv.receiver_id != user_id or inv.status != "Pendiente":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitación no encontrada o no pendiente",
            )

        inv.status = "Aceptada" if accept else "Rechazada"
        self.db.add(inv)

        if accept:
            # Add collaborator GoalUser
            exists = await self.goal_repo.check_collaborator_exists(inv.goal_id, user_id)
            if not exists:
                await self.goal_repo.add_collaborator(inv.goal_id, user_id)

        await self.db.commit()
        await self.db.refresh(inv)
        return inv

    # --- Dashboard Summary ---
    async def get_dashboard_summary(self, user_id: int, month: int, year: int) -> dict:
        net_worth = await self.get_net_worth(user_id)

        # Monthly cleared incomes
        start_date = datetime(year, month, 1)
        # last day of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        cleared_incomes_res = await self.db.execute(
            select(func.coalesce(func.sum(Income.amount), 0)).where(
                Income.user_id == user_id,
                Income.date >= start_date,
                Income.date < end_date,
                Income.status == "Liquidado",
                Income.is_active == True
            )
        )
        cleared_incomes = Decimal(str(cleared_incomes_res.scalar() or 0.00))

        # Monthly paid expenses
        paid_expenses_res = await self.db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date,
                Expense.status == "Pagado",
                Expense.is_active == True
            )
        )
        paid_expenses = Decimal(str(paid_expenses_res.scalar() or 0.00))

        # Pending debt
        pending_debt = Decimal("0.00")
        debts = await self.debt_repo.get_by_user(user_id)
        for d in debts:
            pending_debt += d.pending_balance

        # Expense by Category
        expenses = await self.expense_repo.get_by_user(user_id, month, year)
        expenses_by_cat = {}
        for ex in expenses:
            cat_name = ex.category.name if ex.category else "Sin Categoría"
            expenses_by_cat[cat_name] = expenses_by_cat.get(cat_name, Decimal("0.00")) + ex.amount

        # Income by Category
        incomes = await self.income_repo.get_by_user(user_id, month, year)
        incomes_by_cat = {}
        for inc in incomes:
            cat_name = inc.category.name if inc.category else "Sin Categoría"
            incomes_by_cat[cat_name] = incomes_by_cat.get(cat_name, Decimal("0.00")) + inc.amount

        # Accounts distribution
        accounts = await self.account_repo.get_by_user(user_id)
        accounts_dist = {}
        for acc in accounts:
            accounts_dist[acc.name] = await self.get_real_balance(acc.id, user_id)

        # Debts by creditor
        debts_by_creditor = {}
        for d in debts:
            debts_by_creditor[d.creditor] = debts_by_creditor.get(d.creditor, Decimal("0.00")) + d.pending_balance

        return {
            "net_worth": net_worth,
            "cleared_incomes": cleared_incomes,
            "paid_expenses": paid_expenses,
            "pending_debt": pending_debt,
            "expenses_by_category": {k: float(v) for k, v in expenses_by_cat.items()},
            "incomes_by_category": {k: float(v) for k, v in incomes_by_cat.items()},
            "accounts_distribution": {k: float(v) for k, v in accounts_dist.items()},
            "debts_by_creditor": {k: float(v) for k, v in debts_by_creditor.items()},
            "monthly_balance": {
                "incomes": float(cleared_incomes),
                "expenses": float(paid_expenses)
            }
        }
