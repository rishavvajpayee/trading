import datetime
from datetime import timedelta
from database.config import User
from fastapi import HTTPException
from database.model import UserCreate


def verify(db, user: UserCreate):
    """
    Verify the OTP
    """
    try:
        user_data: User = db.query(User).filter_by(email=user.email).first()
        given_datetime_str = user_data.created_at

        try:
            if user.otp != user_data.otp:
                raise HTTPException(status_code=400, detail="Otp Did Not Match")

            given_datetime = datetime.datetime.strptime(
                given_datetime_str, "%Y-%m-%d %H:%M:%S.%f"
            )
            current_datetime = datetime.datetime.now()
            two_minutes_ago = current_datetime - timedelta(minutes=1)
            time_difference = given_datetime - two_minutes_ago

            if (
                time_difference.total_seconds() < 120
                and time_difference.total_seconds() > 0
            ):
                db.query(User).filter_by(email=user.email).update({"status": True})
                db.commit()
                return {"message": "Email confirmed successfully"}

            else:
                db.query(User).filter_by(email=user.email).update({"status": False})
                db.commit()
                return {"Status": "Time Expired"}

        except Exception as error:
            raise Exception(error)

    except Exception as error:
        raise Exception(error)
