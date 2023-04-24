from pydantic import BaseModel, EmailStr

class Bot(BaseModel):
    loss : float
    profit : float
    number_of_trades : int
    ticker : str
    amount : float
    exchange : str