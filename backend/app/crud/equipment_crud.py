from sqlalchemy.orm import session
from sqlalchemy import select

from app.db.models.equipment_model import Equipment


def get_equipment_by_id(session:session,id:int) -> Equipment | None:
    stmt = select(Equipment).where(Equipment.id == id)
    return session.scalar(stmt)

def list_all_equipment(session:session) -> list[Equipment]:
    stmt = select(Equipment)
    return session.scalars(stmt).all()


if __name__=="__main__":
    from app.db.session import SessionLocal
    session = SessionLocal()
    print(list_all_equipment(session))