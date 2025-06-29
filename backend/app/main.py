from fastapi import FastAPI
from .database import Base, engine
from .routers import groups, expenses, balances

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(groups.router)
app.include_router(expenses.router)
app.include_router(balances.router)