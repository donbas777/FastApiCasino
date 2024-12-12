from sqlalchemy import Column, Integer, String
from sqladmin import ModelView
from app.db.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    balance = Column(Integer, default=0)
    token = Column(String, nullable=True)

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username,User.email]
    column_searchable_list = ["username", "email"]
    column_filters = ["username", "email", "balance"]
