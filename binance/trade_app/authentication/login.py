
import os
import jwt
import random
import smtplib
from database.config import User
from fastapi import HTTPException
from dotenv import load_dotenv
from email.mime.text import MIMEText


load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

def logincheck(db, user, db_user):
    """
    checks the login functionality
    """

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")
    
    user_password = db_user.password
    payload1 = {
        "password":user.password
    }

    encoded_password = jwt.encode(payload1,key=SECRET_KEY,algorithm="HS256")
    
    if encoded_password != user_password:
        raise HTTPException(status_code=400, detail="Invalid password")

    """
    generate OTp and save it to Database
    """
    try:
        otp = random.randint(1000, 9999)
        """ OTP SEND can be sent here """
        db_user.otp = otp
        db.commit()
    
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"{error}")
    
    return db_user


def send_otp(to_email):
    """
    Send OTP utility function that sends
    OTP to the Email being registered / logged in
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv('Admin_email')
    smtp_password =os.getenv('Admin_password')

    otp = random.randint(1000, 9999)

    message = MIMEText(f"Your OTP is: {otp}")
    message["Subject"] = "OTP Verification"
    message["From"] = smtp_username
    message["To"] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, message.as_string())
            print("send OPT= ",otp)
            return otp

    except Exception as e:
        return {"Status": f"Exception Occurred as {e}"}
