from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import BorrowRecordStatus, BorrowReturnStatus, ItemStatusCode, RepairOrderStatus, RepairReportStatus
from app.core.exceptions import BussinessException
from app.crud import borrow_record_crud, borrow_return_image_crud, borrow_return_record_crud, equipment_crud, repair_order_crud, repair_report_crud
from app.db.models.borrow_record_model import BorrowRecord
from app.db.models.borrow_return_image_model import BorrowReturnImage
from app.db.models.borrow_return_record_model import BorrowReturnRecord
from app.db.models.repair_order_model import RepairOrder
from app.db.models.repair_report_model import RepairReport
from app.schema.borrow_record_schema import BorrowRecordCreate, BorrowRecordCreateOut, BorrowRecordOut, BorrowRecordPageOut, BorrowRecordQuery
from app.schema.borrow_return_schema import BorrowReturnCreate, BorrowReturnCreateOut


def create_borrow_record_service(
    session: Session,
    user_id: int,
    borrow_record_in: BorrowRecordCreate,
) -> BorrowRecordCreateOut:
    with session.begin():
        # 锁定设备行，避免并发申请时重复占用同一设备。
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

        # 创建待审核借用记录，并把设备切换为借用审核中。
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
    # 按当前学生 ID 查询借用记录及列表展示所需的设备名称。
    res = borrow_record_crud.query_borrow_record_by_user(session, user_id, query)
    for borrow_record, equipment in res.items:
        borrow_record_out = BorrowRecordPageOut.model_validate(borrow_record)
        borrow_record_out.equipment_name = equipment.equipment_name if equipment else None
        list.append(borrow_record_out)
    # 保留分页器元数据并返回精简列表模型。
    return Page(items=list, total=res.total, page=query.page, size=res.size, pages=res.pages)


def get_borrow_record_detail_by_user_service(
    session: Session,
    borrow_record_id: int,
    user_id: int,
) -> BorrowRecordOut:
    # 查询时同时按借用记录 ID 和当前学生 ID 过滤，隔离他人数据。
    borrow_record_detail = borrow_record_crud.get_borrow_record_detail_by_id_and_user(
        session,
        borrow_record_id,
        user_id,
    )
    if not borrow_record_detail:
        raise BussinessException("借用记录不存在", status_code=404)

    # 补齐详情展示所需的设备和分类字段。
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


def create_borrow_return_record_service(
    session: Session,
    borrow_record_id: int,
    user_id: int,
    borrow_return_in: BorrowReturnCreate,
) -> BorrowReturnCreateOut:
    with session.begin():
        # 锁定并校验当前学生的借用记录，防止重复归还。
        borrow_record = borrow_record_crud.get_borrow_record_by_id_and_user_for_update(
            session,
            borrow_record_id,
            user_id,
        )
        if not borrow_record:
            raise BussinessException("借用记录不存在", status_code=404)
        if borrow_record.status != BorrowRecordStatus.BORROWED:
            raise BussinessException("当前借用记录不能提交归还", status_code=400)
        if borrow_return_record_crud.get_borrow_return_record_by_borrow_record_id(session, borrow_record_id):
            raise BussinessException("该借用记录已提交归还", status_code=409)

        # 锁定关联设备，保证归还状态与设备状态同步更新。
        equipment = equipment_crud.get_equipment_by_id_for_update(session, borrow_record.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)

        # 创建归还主记录，归还图片作为一对多子记录保存。
        borrow_return_record = BorrowReturnRecord(
            return_status=borrow_return_in.return_status,
            return_remark=borrow_return_in.return_remark,
            damage_description=borrow_return_in.damage_description,
            borrow_record_id=borrow_record_id,
        )
        borrow_return_record_crud.add_borrow_return_record(borrow_return_record, session)
        for sort, image_url in enumerate(borrow_return_in.damage_images):
            borrow_return_image_crud.add_borrow_return_image(
                BorrowReturnImage(
                    return_record_id=borrow_return_record.id,
                    image_url=image_url,
                    sort=sort,
                ),
                session,
            )

        # 损坏归还自动生成报修记录和待派单维修工单。
        if borrow_return_in.return_status == BorrowReturnStatus.DAMAGED:
            repair_report = RepairReport(
                return_record_id=borrow_return_record.id,
                user_id=user_id,
                equipment_id=borrow_record.equipment_id,
                damage_description=borrow_return_in.damage_description,
                status=RepairReportStatus.PENDING,
            )
            repair_report_crud.add_repair_report(repair_report, session)
            repair_order_crud.add_repair_order(
                RepairOrder(
                    repair_report_id=repair_report.id,
                    equipment_id=borrow_record.equipment_id,
                    status=RepairOrderStatus.PENDING_ASSIGN,
                ),
                session,
            )

        # 学生归还立即完成借用；损坏归还则将设备转入待维修。
        borrow_record_crud.update_borrow_record(
            borrow_record,
            {"status": BorrowRecordStatus.COMPLETED},
            session,
        )
        equipment_crud.update_equipment(
            equipment,
            {
                "status": (
                    ItemStatusCode.REPAIR_PENDING
                    if borrow_return_in.return_status == BorrowReturnStatus.DAMAGED
                    else ItemStatusCode.AVAILABLE
                )
            },
            session,
        )
        # 使用已 flush 的归还记录回显，并补充本次上传的图片地址。
        borrow_return_out = BorrowReturnCreateOut.model_validate(borrow_return_record)
        borrow_return_out.damage_images = borrow_return_in.damage_images
        return borrow_return_out
        # 校验设备当前可借用，再检查申请时间段是否冲突。
