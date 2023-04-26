from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class BotModel(BaseModel):
    loss : float
    profit : float
    number_of_trades : int
    ticker : str
    amount : float
    exchange : str

class UserModel(BaseModel):
    username : str
    password : str

class Data(BaseModel):
    username : str


