from sqlalchemy import Insert
from sqlalchemy.orm import Session

from app.db.models.user_model import User


def add_user(user: User, db: Session):
    db.add(user)
    db.flush()
    return None


def query_user_by_username(username, db: Session) -> User | None:
    return db.query(User).filter(User.username == username).first()