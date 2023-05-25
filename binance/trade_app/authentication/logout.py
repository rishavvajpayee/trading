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
    


