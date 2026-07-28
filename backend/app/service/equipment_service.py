from app.crud.equipment_crud import list_all_equipment, get_all_equipment_out
from app.db.session import SessionLocal
from app.schema.equipment_schema import EquipmentOut
from app.schema.page_schema import PageResp


def get_all_equipment(session: SessionLocal) -> PageResp[EquipmentOut]:
    list = []
    for e,c in get_all_equipment_out(session):
        equip_out = EquipmentOut.model_validate(e)
        equip_out.category_name = c.category_name if c else None
        list.append(equip_out)
    return PageResp(total=len(list), records=list)