from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

group_users = Table(
    'group_users', Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    users = relationship("User", secondary=group_users, backref="groups")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Float)
    paid_by = Column(Integer, ForeignKey("users.id"))
    split_type = Column(String)
    splits = Column(String)  # Store as JSON string (for % splits)
    group_id = Column(Integer, ForeignKey("groups.id"))