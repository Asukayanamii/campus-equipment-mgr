from sqlalchemy.orm import Session

from app.db.models.equipment_status_record_model import EquipmentStatusRecord


def add_equipment_status_record(equipment_status_record: EquipmentStatusRecord, session: Session) -> None:
    session.add(equipment_status_record)
    session.flush()
