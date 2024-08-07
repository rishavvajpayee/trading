from pydantic import BaseModel
from pydantic import EmailStr


class Database(BaseModel):
    """
    db model
    """

    bot_id: str
    buy_value: float or None = None # type: ignore
    sell_value: float or None = None
    pnl: float or None = None


class BotModel(BaseModel):
    """
    Bot Model called for API DATA
    """

    loss: float
    profit: float
    number_of_trades: int
    ticker: str
    exchange: str
    price: float


class UserModel(BaseModel):
    """
    User Model calls when filling the DB with USER DATA
    """

    email: str
    username: str
    password: str


class Data(BaseModel):
    """
    Used while calling "/data" endpoint
    """

    username: str


class UserCreate(BaseModel):
    """
    Model used to create a user
    """

    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """
    model used for user login
    """

    email: EmailStr
    password: str


class Verify(BaseModel):
    """
    model used to verify user
    """

    email: EmailStr
    otp: str
