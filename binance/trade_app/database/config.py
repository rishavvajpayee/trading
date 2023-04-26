from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker
from sqlalchemy.sql import func
import psycopg2

engine = create_engine("postgresql://root:root@localhost/axxon")
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind = engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index = True)
    email = EmailStr
    username = Column(String)
    password = Column(String)
    bots = relationship("Bot", back_populates="owner")

class Bot(Base):
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, index = True)
    bot_ids = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="bots")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind = engine)


