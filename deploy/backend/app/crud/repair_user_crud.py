from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.db.models.repair_user_model import RepairUser
from app.schema.common_schema import PageQuery


def add_repair_user(repair_user: RepairUser, db: Session) -> None:
    db.add(repair_user)
    db.flush()
    return None


def query_repair_user_by_username(username, db: Session) -> RepairUser | None:
    return db.query(RepairUser).filter(RepairUser.username == username).first()


def get_repair_user_by_id(id: int, db: Session) -> RepairUser | None:
    return db.query(RepairUser).filter(RepairUser.id == id).first()


def update_repair_user(update_model: RepairUser, db: Session) -> None:
    data = {}
    if update_model.update_time:
        data['update_time'] = update_model.update_time
    if update_model.name:
        data['name'] = update_model.name
    if update_model.password:
        data['password'] = update_model.password
    if update_model.image:
        data['image'] = update_model.image
    db.query(RepairUser).where(RepairUser.id == update_model.id).update(data)


def query_repair_users(session: Session, query: PageQuery) -> Page[RepairUser]:
    stmt = select(RepairUser).order_by(asc(RepairUser.id))
    return paginate(session, stmt, query)
