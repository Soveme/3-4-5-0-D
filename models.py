# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
# from sqlalchemy.orm import relationship
# from database import Base
# from datetime import datetime
#
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)
#     expenses = relationship("Expense", back_populates="owner")
#     groups = relationship("Group", secondary="group_members", back_populates="members")
#     created_groups = relationship("Group", back_populates="admin")
#
# class Category(Base):
#     __tablename__ = "categories"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
#     expenses = relationship("Expense", back_populates="category")
#
# class Expense(Base):
#     __tablename__ = "expenses"
#     id = Column(Integer, primary_key=True, index=True)
#     amount = Column(Float)
#     category_id = Column(Integer, ForeignKey("categories.id"))
#     date = Column(DateTime, default=datetime.now)
#     description = Column(String, nullable=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
#     owner = relationship("User", back_populates="expenses")
#     category = relationship("Category", back_populates="expenses")
#     group = relationship("Group", back_populates="expenses")
#
# class Budget(Base):
#     __tablename__ = "budgets"
#     id = Column(Integer, primary_key=True, index=True)
#     category_id = Column(Integer, ForeignKey("categories.id"))
#     amount = Column(Float)
#     period = Column(String)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
#     group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
#
# class Group(Base):
#     __tablename__ = "groups"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     admin_id = Column(Integer, ForeignKey("users.id"))
#     admin = relationship("User", back_populates="created_groups")
#     members = relationship("User", secondary="group_members", back_populates="groups")
#     expenses = relationship("Expense", back_populates="group")
#     budgets = relationship("Budget")
#
# class GroupMember(Base):
#     __tablename__ = "group_members"
#     user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
#     group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)