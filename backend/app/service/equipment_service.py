from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import AuditBusinessType, ITEM_STATUS_MAP
from app.core.config import settings
from app.core.exceptions import BussinessException
from app.crud import equipment_crud, equipment_status_record_crud
from app.db.models.equipment_model import Equipment
from app.db.models.equipment_status_record_model import EquipmentStatusRecord
from app.schema.equipment_schema import EquipmentCreate, EquipmentOut, EquipmentUpdate, EquipQuery
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
    # 执行设备与分类的分页联表查询。
    res = equipment_crud.query_equipment(session,query)
    # 补充分类名称并将设备状态编码转换为展示含义。
    for e,c in res.items:
        equip_out = EquipmentOut.model_validate(e)
        equip_out.category_name = c.category_name if c else None
        equip_out.status = ITEM_STATUS_MAP.get(equip_out.status, equip_out.status)
        list.append(equip_out)
    # 保留分页器的元数据并返回转换后的列表。
    return Page(items=list, total=res.total, page=query.page, size=res.size, pages=res.pages)


def get_equipment_service(session: Session, equipment_id: int) -> EquipmentOut:
    # 查询未删除设备及其分类信息。
    equipment_detail = equipment_crud.get_equipment_detail_by_id(session, equipment_id)
    if not equipment_detail:
        raise BussinessException("设备不存在", status_code=404)

    # 组装详情响应并转换设备状态展示值。
    equipment, category = equipment_detail
    equipment_out = EquipmentOut.model_validate(equipment)
    equipment_out.category_name = category.category_name if category else None
    equipment_out.status = ITEM_STATUS_MAP.get(equipment_out.status, equipment_out.status)
    return equipment_out


def create_equipment_service(session: Session, equipment_in: EquipmentCreate) -> None:
    with session.begin():
        # 校验资产编号的全局唯一性。
        if equipment_crud.get_equipment_by_no(session, equipment_in.equipment_no):
            raise BussinessException("设备编号已存在", status_code=409)
        # 补充未传封面时的默认图片。
        equipment_data = equipment_in.model_dump()
        if not equipment_data["cover_img"]:
            equipment_data["cover_img"] = settings.DEFAULT_EQUIPMENT_IMAGE_URL
        # 在当前事务中写入设备。
        equipment_crud.add_equipment(Equipment(**equipment_data), session)


def change_equipment_status_service(
    session: Session,
    equipment: Equipment,
    target_status: str,
    business_type: str,
    business_id: int,
    admin_id: int,
    reason: str | None = None,
) -> bool:
    """更新设备状态；仅状态实际变化时写入状态变更记录。"""
    if equipment.status == target_status:
        return False

    # 保存变更前状态，并在当前事务中同步更新设备和状态历史。
    before_status = equipment.status
    equipment_crud.update_equipment(equipment, {"status": target_status}, session)
    equipment_status_record_crud.add_equipment_status_record(
        EquipmentStatusRecord(
            equipment_id=equipment.id,
            before_status=before_status,
            after_status=target_status,
            business_type=business_type,
            business_id=business_id,
            operator_id=admin_id,
            reason=reason,
        ),
        session,
    )
    return True


def update_equipment_service(
    session: Session,
    equipment_id: int,
    equipment_in: EquipmentUpdate,
    admin_id: int,
) -> None:
    with session.begin():
        # 确认目标设备存在且未被逻辑删除。
        equipment = equipment_crud.get_equipment_by_id_for_update(session, equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)

        # 仅提取请求中显式传入的更新字段。
        values = equipment_in.model_dump(exclude_unset=True)
        equipment_no = values.get("equipment_no")
        if equipment_no:
            same_no_equipment = equipment_crud.get_equipment_by_no(session, equipment_no)
            if same_no_equipment and same_no_equipment.id != equipment_id:
                raise BussinessException("设备编号已存在", status_code=409)
        # 普通信息字段按原逻辑更新，不写设备状态变更历史。
        target_status = values.pop("status", None)
        if values:
            equipment_crud.update_equipment(equipment, values, session)
        # 仅请求状态实际改变时，统一更新设备状态并记录状态历史。
        if target_status is not None:
            change_equipment_status_service(
                session=session,
                equipment=equipment,
                target_status=target_status,
                business_type=AuditBusinessType.EQUIPMENT,
                business_id=equipment.id,
                admin_id=admin_id,
            )


def delete_equipment_service(session: Session, equipment_id: int) -> None:
    with session.begin():
        # 确认设备存在后执行逻辑删除。
        equipment = equipment_crud.get_equipment_by_id(session, equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)
        equipment_crud.delete_equipment(equipment, session)
