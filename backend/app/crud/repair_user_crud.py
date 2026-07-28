from sqlalchemy.orm import Session

from app.db.models.repair_user_model import RepairUser


def add_repair_user(repair_user: RepairUser, db: Session):
    db.add(repair_user)
    db.flush()
    return None


def query_repair_user_by_username(username, db: Session) -> RepairUser | None:
    return db.query(RepairUser).filter(RepairUser.username == username).first()
