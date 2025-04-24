from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    expenses = relationship("Expense", back_populates="owner")
    groups = relationship("Group", secondary="group_members", back_populates="members")
    created_groups = relationship("Group", back_populates="admin")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"))
    date = Column(Date)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="expenses")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Float)
    period = Column(String)
    category = relationship("Category")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    admin_id = Column(Integer, ForeignKey("users.id"))
    admin = relationship("User", back_populates="created_groups")
    members = relationship("User", secondary="group_members", back_populates="groups")

class GroupMember(Base):
    __tablename__ = "group_members"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)