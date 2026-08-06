from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import BorrowRecordStatus, ItemStatusCode
from app.core.exceptions import BussinessException
from app.crud import borrow_record_crud, equipment_crud
from app.db.models.borrow_record_model import BorrowRecord
from app.schema.borrow_record_schema import BorrowRecordCreate, BorrowRecordOut, BorrowRecordPageOut, BorrowRecordQuery


def create_borrow_record_service(
    session: Session,
    user_id: int,
    borrow_record_in: BorrowRecordCreate,
) -> BorrowRecordOut:
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
        return BorrowRecordOut.model_validate(borrow_record)


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
