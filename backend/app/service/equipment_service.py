from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.crud.equipment_crud import list_all_equipment, query_equipment
from app.schema.equipment_schema import EquipmentOut, EquipQuery
from app.schema.page_schema import PageResp


# def get_all_equipment(session: Session) -> PageResp[EquipmentOut]:
#     list = []
#     for e,c in get_all_equipment_out(session):
#         equip_out = EquipmentOut.model_validate(e)
#         equip_out.category_name = c.category_name if c else None
#         list.append(equip_out)
#     return PageResp(total=len(list), records=list)

def query_equipment_service(session: Session, query: EquipQuery) -> Page[EquipmentOut]:
    list = []
    res = query_equipment(session,query)
    # 转换成EquipmentOut
    for e,c in res.items:
        equip_out = EquipmentOut.model_validate(e)
        equip_out.category_name = c.category_name if c else None
        list.append(equip_out)
    # 返回Page
    return Page(items=list, total=res.total, page=query.page, size=res.size, pages=res.pages)