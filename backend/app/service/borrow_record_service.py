from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import BorrowRecordStatus, ItemStatusCode
from app.core.exceptions import BussinessException
from app.crud import borrow_record_crud, equipment_crud
from app.db.models.borrow_record_model import BorrowRecord
from app.schema.borrow_record_schema import BorrowRecordCreate, BorrowRecordCreateOut, BorrowRecordOut, BorrowRecordPageOut, BorrowRecordQuery


def create_borrow_record_service(
    session: Session,
    user_id: int,
    borrow_record_in: BorrowRecordCreate,
) -> BorrowRecordCreateOut:
    with session.begin():
        equipment = equipment_crud.get_equipment_by_id_for_update(session, borrow_record_in.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)
        if equipment.status != ItemStatusCode.AVAILABLE:
            raise BussinessException("当前设备不可借用", status_code=400)

        borrow_record = borrow_record_crud.get_borrow_record_by_equipment_time(
            session,
            borrow_record_in.equipment_id,
            borrow_record_in.borrow_start_time,
            borrow_record_in.borrow_end_time,
        )
        if borrow_record:
            raise BussinessException("该时间段内设备已被申请借用", status_code=409)

        borrow_record = BorrowRecord(
            **borrow_record_in.model_dump(),
            user_id=user_id,
            status=BorrowRecordStatus.PENDING,
        )
        borrow_record_crud.add_borrow_record(borrow_record, session)
        equipment_crud.update_equipment(equipment, {"status": ItemStatusCode.PENDING_BORROW}, session)
        return BorrowRecordCreateOut.model_validate(borrow_record)


def query_borrow_record_by_user_service(
    session: Session,
    user_id: int,
    query: BorrowRecordQuery,
) -> Page[BorrowRecordPageOut]:
    list = []
    res = borrow_record_crud.query_borrow_record_by_user(session, user_id, query)
    for borrow_record, equipment in res.items:
        borrow_record_out = BorrowRecordPageOut.model_validate(borrow_record)
        borrow_record_out.equipment_name = equipment.equipment_name if equipment else None
        list.append(borrow_record_out)
    return Page(items=list, total=res.total, page=query.page, size=res.size, pages=res.pages)


def get_borrow_record_detail_by_user_service(
    session: Session,
    borrow_record_id: int,
    user_id: int,
) -> BorrowRecordOut:
    borrow_record_detail = borrow_record_crud.get_borrow_record_detail_by_id_and_user(
        session,
        borrow_record_id,
        user_id,
    )
    if not borrow_record_detail:
        raise BussinessException("借用记录不存在", status_code=404)

    borrow_record, equipment, category = borrow_record_detail
    borrow_record_out = BorrowRecordOut.model_validate(borrow_record)
    if equipment:
        borrow_record_out.equipment_no = equipment.equipment_no
        borrow_record_out.equipment_name = equipment.equipment_name
        borrow_record_out.category_id = equipment.category_id
        borrow_record_out.category_name = category.category_name if category else None
        borrow_record_out.spec = equipment.spec
        borrow_record_out.brand = equipment.brand
        borrow_record_out.unit = equipment.unit
        borrow_record_out.location = equipment.location
        borrow_record_out.purchase_date = equipment.purchase_date
        borrow_record_out.price = equipment.price
        borrow_record_out.cover_img = equipment.cover_img
        borrow_record_out.equipment_status = equipment.status
        borrow_record_out.remark = equipment.remark
    return borrow_record_out
