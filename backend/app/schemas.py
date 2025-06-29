from pydantic import BaseModel
from typing import List, Optional, Dict

class UserCreate(BaseModel):
    name: str

class GroupCreate(BaseModel):
    name: str
    user_ids: List[int]

class GroupOut(BaseModel):
    id: int
    name: str
    user_ids: List[int]
    class Config:
        orm_mode = True

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    paid_by: int
    split_type: str
    splits: Optional[Dict[int, float]] = None

class ExpenseOut(BaseModel):
    id: int
    description: str
    amount: float
    paid_by: int
    split_type: str
    group_id: int

class BalanceOut(BaseModel):
    user_id: int
    balance: float