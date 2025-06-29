from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter()   # <---- THIS LINE MUST BE FIRST

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/groups", response_model=schemas.GroupOut)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    # Fetch all users at once, ensure all are present
    user_objs = db.query(models.User).filter(models.User.id.in_(group.user_ids)).all()
    if len(user_objs) != len(group.user_ids):
        raise HTTPException(status_code=400, detail="One or more user_ids not found")

    db_group = models.Group(name=group.name)
    db_group.users = user_objs
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return schemas.GroupOut(
        id=db_group.id,
        name=db_group.name,
        user_ids=[user.id for user in db_group.users]
    )