from sqlalchemy import Insert
from sqlalchemy.orm import Session

from app.db.models.user_model import User


def add_user(user: User, db: Session):
    db.add(user)
    db.flush()
    return None


def query_user_by_username(username, db: Session) -> User | None:
    return db.query(User).filter(User.username == username).first()


def query_user_by_email(email: str, db: Session) -> User | None:
    """按邮箱查询学生账号，用于邮箱验证码注册和登录。"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(id: int, db: Session) -> User | None:
    return db.query(User).filter(User.id == id).first()


def update_user(update_model: User, db: Session) -> None:
    data = {}
    if update_model.update_time:
        data['update_time'] = update_model.update_time
    if update_model.name:
        data['name'] = update_model.name
    if update_model.password:
        data['password'] = update_model.password
    if update_model.image:
        data['image'] = update_model.image
    db.query(User).where(User.id == update_model.id).update(data)


def update_user_email(user: User, email: str, db: Session) -> None:
    """更新当前学生已通过验证码校验的邮箱。"""
    user.email = email
    db.flush()
