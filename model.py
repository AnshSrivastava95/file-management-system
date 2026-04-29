from sqlalchemy import Column,Integer,String
from database import Base

class user(Base):
    __tablename__="users"
    id=Column(Integer,index=True,primary_key=True)
    email=Column(String,unique=True,index=True)
    password=Column(String)
    role=Column(String,default="user")