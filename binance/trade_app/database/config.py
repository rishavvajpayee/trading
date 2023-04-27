import os
from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

load_dotenv()

"""
Create database engine
"""

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind = engine)
Base = declarative_base()

class User(Base):
    """
    user database table
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index = True)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    otp = Column(String, nullable=True)
    created_at = Column(String)
    bots = relationship("Bot", back_populates="owner",  cascade="all, delete-orphan")

class Bot(Base):
    """
    Bot database table
    """
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, index = True)
    bot_ids = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="bots")

def get_db():
    """ utility function that gets the local DB Session """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


""" Create the Base metadata """
Base.metadata.create_all(bind = engine)


