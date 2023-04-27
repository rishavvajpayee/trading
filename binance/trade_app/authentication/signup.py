import jwt
import os
from datetime import datetime
from dotenv import load_dotenv
from database.config import User

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

def create_user(db, user):
    if len(user.password)>=8:
        payload={
            "password":user.password
        }
        encoded_data = jwt.encode(payload,key=SECRET_KEY,algorithm="HS256") #use SHA-256 or MD5
        current_datetime = datetime.now()
        try :
            db_user = User(username=user.username, email=user.email, password=encoded_data, created_at = current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return {
                "status" : "user created",
                "email" : db_user.email,
                "username" : db_user.username,
            }
        
        except Exception as error:
            return {
                "Status": "Creatiion failed"
            }
    else:
        return {
            "Status": "Password length should be 8 characters"
        }