from app.crud.equipment_crud import list_all_equipment
from app.db.session import SessionLocal
from app.schema.equipment_schema import EquipmentOut


def get_all_equipment(session: SessionLocal) -> list[EquipmentOut]:
    all_equipment = [EquipmentOut.model_validate(i) for i in list_all_equipment(session)]
    return all_equipment