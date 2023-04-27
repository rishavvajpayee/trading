from pydantic import BaseModel
from pydantic import EmailStr

class BotModel(BaseModel):
    """
    Bot Model called for API DATA
    """
    loss : float
    profit : float
    number_of_trades : int
    ticker : str
    amount : float
    exchange : str

class UserModel(BaseModel):
    """
    User Model calls when filling the DB with USER DATA
    """
    email : str
    username : str
    password : str

class Data(BaseModel):
    """
    Used while calling "/data" endpoint
    """
    username : str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Verify(BaseModel):
    email: EmailStr
    otp: str
