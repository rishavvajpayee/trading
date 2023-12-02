from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import Request
from fastapi import HTTPException
from database.config import User
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, WebSocket, Depends, Request


def logout(request: Request):
    """
    Logout the user and clear the session.
    """
    session = request.session
    email = session.get("email")
    try:
        if email:
            session.clear()
            return {"message": "Logout Successful"}
        else:
            return HTTPException(status_code=401, detail="User not logged in")
    except Exception as error:
        print(error)
