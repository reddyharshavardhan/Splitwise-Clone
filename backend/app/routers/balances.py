from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_balances(group, db):
    # Initialize balances
    user_ids = [user.id for user in group.users]
    balances = {uid: 0.0 for uid in user_ids}
    expenses = db.query(models.Expense).filter_by(group_id=group.id).all()

    for exp in expenses:
        if exp.split_type == 'equal':
            n = len(user_ids)
            share = exp.amount / n
            for uid in user_ids:
                if uid == exp.paid_by:
                    balances[uid] += exp.amount - share
                else:
                    balances[uid] -= share
        elif exp.split_type == 'percentage':
            splits = exp.splits if hasattr(exp, 'splits') else {}  # You may want to store splits in a separate table or extend Expense.
            total = exp.amount
            # If not present, fallback to equal
            if not splits:
                n = len(user_ids)
                share = total / n
                for uid in user_ids:
                    if uid == exp.paid_by:
                        balances[uid] += total - share
                    else:
                        balances[uid] -= share
            else:
                # splits - dict with string keys (user ids) and float % values
                for uid in user_ids:
                    percent = splits.get(str(uid), 0)
                    owed = total * percent / 100
                    if uid == exp.paid_by:
                        balances[uid] += total - owed
                    else:
                        balances[uid] -= owed
    return balances

@router.get("/groups/{group_id}/balances")
def group_balances(group_id: int, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    balances = calculate_balances(group, db)
    # Turn into "who owes whom" (net balancing)
    results = []
    for uid, amt in balances.items():
        results.append({"user_id": uid, "balance": amt})
    return {"group_id": group_id, "balances": results}


@router.get("/users/{user_id}/balances")
def user_balances(user_id: int, db: Session = Depends(get_db)):
    # All groups user is in
    groups = db.query(models.Group).filter(models.Group.users.any(id=user_id)).all()
    summary = []
    for group in groups:
        balances = calculate_balances(group, db)
        user_balance = balances.get(user_id, 0)
        summary.append({
            "group_id": group.id,
            "group_name": group.name,
            "balance": user_balance
        })
    return {"user_id": user_id, "groups": summary}  