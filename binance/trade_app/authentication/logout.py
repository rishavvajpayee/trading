from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import  Request
from fastapi import HTTPException
from database.config import User
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException ,WebSocket, Depends, Request


def logout(request: Request):
    """
    Logout the user and clear the session.
    """
    session = request.session
    email = session.get("email","")
    print('-----------------',email)
    if email:
        session.clear()
        return JSONResponse(
            status_code = status.HTTP_200_OK,
            content = {"message":"Logout Successful"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in"
        )
    

def delete(request:Request,db):
    """
    Delete the current active User
    """

    session = request.session
    user = db.query(User).filter(User.email == session.get('email')).first()
    print(session.get('email'))
    print(user)
    if user:
        db.delete(user)
        db.commit
        return JSONResponse(
            status_code = status.HTTP_200_OK,
            content = {"message":"Account Deleted"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in"
        )
    

