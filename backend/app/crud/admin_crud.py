from sqlalchemy.orm import Session

from app.db.models.admin_model import Admin


def add_admin(admin: Admin, db: Session):
    db.add(admin)
    db.flush()
    return None


def query_admin_by_username(username, db: Session) -> Admin | None:
    return db.query(Admin).filter(Admin.username == username).first()
