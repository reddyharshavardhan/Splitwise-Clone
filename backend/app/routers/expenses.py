from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/groups/{group_id}/expenses")
def add_expense(
    group_id: int,
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db)
):
    db_group = db.query(models.Group).filter_by(id=group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if expense.paid_by not in [user.id for user in db_group.users]:
        raise HTTPException(status_code=400, detail="Payer not in group users")

    # Check split type
    group_user_ids = [user.id for user in db_group.users]
    if expense.split_type == "equal":
        if set(expense.splits) != set(group_user_ids):
            raise HTTPException(status_code=400, detail="Splits should contain all group users for equal split")
    elif expense.split_type == "percentage":
        percents = expense.splits
        if sorted(percents.keys()) != sorted(map(str, group_user_ids)):
            raise HTTPException(
                status_code=400,
                detail="Splits keys should be string of all group user ids for percentage"
            )
        if abs(sum(percents.values()) - 100.0) > 1e-3:
            raise HTTPException(
                status_code=400,
                detail="Percentage splits must total 100"
            )

    db_expense = models.Expense(
        description=expense.description,
        amount=expense.amount,
        paid_by=expense.paid_by,
        split_type=expense.split_type,
        group_id=group_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    # We'll store split details in a separate Split table for accurate balances, but for now, we'll rely on total expenses.

    return {"status": "Expense added", "id": db_expense.id}