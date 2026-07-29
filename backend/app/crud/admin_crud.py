from sqlalchemy.orm import Session

from app.db.models.admin_model import Admin


def add_admin(admin: Admin, db: Session):
    db.add(admin)
    db.flush()
    return None


def query_admin_by_username(username:  str, db: Session) -> Admin | None:
    return db.query(Admin).filter(Admin.username == username).first()


def get_admin_by_id(id: int,db: Session):
    return db.query(Admin).filter(Admin.id == id).first()


def update_admin(update_model: Admin, db: Session) :
    di = {}
    if update_model.update_time:
        di['update_time'] = update_model.update_time
    if update_model.name:
        di['name'] = update_model.name
    if update_model.password:
        di['password'] = update_model.password
    if update_model.image:
        di['image'] = update_model.image
    db.query( Admin).where(Admin.id == update_model.id).update(di)