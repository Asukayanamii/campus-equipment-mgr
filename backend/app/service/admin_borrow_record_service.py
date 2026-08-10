from datetime import datetime

from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import (
    BorrowRecordStatus,
    BorrowReturnStatus,
    ConfirmStatus,
    ItemStatusCode,
    RepairOrderStatus,
    RepairReportStatus,
)
from app.core.exceptions import BussinessException
from app.crud import (
    borrow_record_crud,
    borrow_return_image_crud,
    borrow_return_record_crud,
    equipment_crud,
    repair_order_crud,
    repair_report_crud,
)
from app.db.models.repair_order_model import RepairOrder
from app.db.models.repair_report_model import RepairReport
from app.schema.admin_borrow_record_schema import (
    AdminBorrowRecordOut,
    AdminBorrowRecordPageOut,
    AdminBorrowRecordQuery,
    BorrowRecordReview,
    BorrowRecordReviewOut,
    BorrowReturnConfirm,
    BorrowReturnConfirmOut,
)
from app.service.equipment_service import change_equipment_status_service


def _build_borrow_record_detail_out(session: Session, borrow_record_detail) -> AdminBorrowRecordOut:
    """将管理端借用记录联查结果转换为详情响应。"""
    borrow_record, user, equipment, category, borrow_return_record, repair_report, repair_order = borrow_record_detail
    borrow_record_out = AdminBorrowRecordOut.model_validate(borrow_record)

    # 补充申请人和设备完整展示信息。
    if user:
        borrow_record_out.user_name = user.name
        borrow_record_out.username = user.username
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

    # 补充学生归还申报、管理员确认和损坏图片信息。
    if borrow_return_record:
        borrow_record_out.return_record_id = borrow_return_record.id
        borrow_record_out.return_status = borrow_return_record.return_status
        borrow_record_out.return_remark = borrow_return_record.return_remark
        borrow_record_out.damage_description = borrow_return_record.damage_description
        borrow_record_out.damage_images = [
            image.image_url
            for image in borrow_return_image_crud.get_borrow_return_images_by_return_record_id(
                session,
                borrow_return_record.id,
            )
        ]
        borrow_record_out.return_time = borrow_return_record.return_time
        borrow_record_out.confirm_status = borrow_return_record.confirm_status
        borrow_record_out.confirmed_status = borrow_return_record.confirmed_status
        borrow_record_out.confirm_remark = borrow_return_record.confirm_remark
        borrow_record_out.confirmer_id = borrow_return_record.confirmer_id
        borrow_record_out.confirm_time = borrow_return_record.confirm_time

    # 补充关联报修和维修工单摘要。
    if repair_report:
        borrow_record_out.repair_report_id = repair_report.id
        borrow_record_out.repair_report_status = repair_report.status
    if repair_order:
        borrow_record_out.repair_order_id = repair_order.id
        borrow_record_out.repair_order_status = repair_order.status
    return borrow_record_out


def query_borrow_record_by_admin_service(
    session: Session,
    query: AdminBorrowRecordQuery,
) -> Page[AdminBorrowRecordPageOut]:
    records = []
    # 分页联查申请人、设备和归还记录，组装管理端列表展示字段。
    res = borrow_record_crud.query_borrow_record_by_admin(session, query)
    for borrow_record, user, equipment, borrow_return_record in res.items:
        borrow_record_out = AdminBorrowRecordPageOut.model_validate(borrow_record)
        borrow_record_out.user_name = user.name if user else None
        borrow_record_out.username = user.username if user else None
        borrow_record_out.equipment_name = equipment.equipment_name if equipment else None
        borrow_record_out.return_status = borrow_return_record.return_status if borrow_return_record else None
        borrow_record_out.confirm_status = borrow_return_record.confirm_status if borrow_return_record else None
        borrow_record_out.confirmed_status = borrow_return_record.confirmed_status if borrow_return_record else None
        records.append(borrow_record_out)
    # 保留分页器元数据并返回展示模型。
    return Page(items=records, total=res.total, page=query.page, size=res.size, pages=res.pages)


def get_borrow_record_detail_by_admin_service(
    session: Session,
    borrow_record_id: int,
) -> AdminBorrowRecordOut:
    # 查询借用记录及其申请人、设备、归还、报修和工单关联信息。
    borrow_record_detail = borrow_record_crud.get_borrow_record_detail_by_id_for_admin(session, borrow_record_id)
    if not borrow_record_detail:
        raise BussinessException("借用记录不存在", status_code=404)
    # 统一组装详情响应，保证状态字段在序列化时转换为展示含义。
    return _build_borrow_record_detail_out(session, borrow_record_detail)


def review_borrow_record_service(
    session: Session,
    borrow_record_id: int,
    admin_id: int,
    review_in: BorrowRecordReview,
) -> BorrowRecordReviewOut:
    with session.begin():
        # 锁定借用记录并限制为待审核状态，避免重复审核。
        borrow_record = borrow_record_crud.get_borrow_record_by_id_for_update(session, borrow_record_id)
        if not borrow_record:
            raise BussinessException("借用记录不存在", status_code=404)
        if borrow_record.status != BorrowRecordStatus.PENDING:
            raise BussinessException("当前借用记录不能审核", status_code=400)

        # 锁定关联设备，确保审核结果和设备状态同步提交。
        equipment = equipment_crud.get_equipment_by_id_for_update(session, borrow_record.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)
        result_status = BorrowRecordStatus.BORROWED if review_in.approved else BorrowRecordStatus.REJECTED
        equipment_status = ItemStatusCode.BORROWED if review_in.approved else ItemStatusCode.AVAILABLE
        borrow_record_crud.update_borrow_record(
            borrow_record,
            {"status": result_status, "review_remark": review_in.review_remark},
            session,
        )
        change_equipment_status_service(
            session=session,
            equipment=equipment,
            target_status=equipment_status,
        )
        return BorrowRecordReviewOut.model_validate(borrow_record)


def confirm_borrow_return_service(
    session: Session,
    borrow_record_id: int,
    admin_id: int,
    confirm_in: BorrowReturnConfirm,
) -> BorrowReturnConfirmOut:
    with session.begin():
        # 锁定借用记录并限制为待确认归还状态，防止重复确认。
        borrow_record = borrow_record_crud.get_borrow_record_by_id_for_update(session, borrow_record_id)
        if not borrow_record:
            raise BussinessException("借用记录不存在", status_code=404)
        if borrow_record.status != BorrowRecordStatus.PENDING_RETURN:
            raise BussinessException("当前借用记录不能确认归还", status_code=400)

        # 锁定归还记录和设备，保证归还确认、维修流程、设备状态原子一致。
        borrow_return_record = borrow_return_record_crud.get_borrow_return_record_by_borrow_record_id_for_update(
            session,
            borrow_record_id,
        )
        if not borrow_return_record:
            raise BussinessException("归还记录不存在", status_code=404)
        if borrow_return_record.confirm_status != ConfirmStatus.PENDING:
            raise BussinessException("当前归还记录已确认", status_code=400)
        equipment = equipment_crud.get_equipment_by_id_for_update(session, borrow_record.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)

        # 根据管理员最终判定维护报修和维修工单，避免学生申报与最终验收不一致。
        repair_report = repair_report_crud.get_repair_report_by_return_record_id(session, borrow_return_record.id)
        if confirm_in.confirmed_status == BorrowReturnStatus.DAMAGED:
            if not repair_report:
                repair_report = RepairReport(
                    return_record_id=borrow_return_record.id,
                    user_id=borrow_record.user_id,
                    equipment_id=borrow_record.equipment_id,
                    damage_description=(
                        borrow_return_record.damage_description
                        or confirm_in.confirm_remark
                        or "管理员验收发现设备损坏"
                    ),
                    status=RepairReportStatus.CONFIRMED,
                )
                repair_report_crud.add_repair_report(repair_report, session)
            else:
                repair_report_crud.update_repair_report(
                    repair_report,
                    {
                        "status": RepairReportStatus.CONFIRMED,
                    },
                    session,
                )
            if not repair_order_crud.get_repair_order_by_repair_report_id(session, repair_report.id):
                repair_order_crud.add_repair_order(
                    RepairOrder(
                        repair_report_id=repair_report.id,
                        equipment_id=borrow_record.equipment_id,
                        status=RepairOrderStatus.PENDING_ASSIGN,
                    ),
                    session,
                )
            target_equipment_status = ItemStatusCode.REPAIR_PENDING
        else:
            if repair_report:
                repair_report_crud.update_repair_report(
                    repair_report,
                    {
                        "status": RepairReportStatus.REJECTED,
                    },
                    session,
                )
                repair_order = repair_order_crud.get_repair_order_by_repair_report_id(session, repair_report.id)
                if repair_order and repair_order.status in (
                    RepairOrderStatus.PENDING_ASSIGN,
                    RepairOrderStatus.PENDING_REPAIR,
                ):
                    repair_order_crud.update_repair_order(
                        repair_order,
                        {"status": RepairOrderStatus.CANCELLED},
                        session,
                    )
            target_equipment_status = ItemStatusCode.AVAILABLE

        # 回写管理员确认结果，并同步完成借用记录和设备状态。
        confirm_time = datetime.now()
        borrow_return_record_crud.update_borrow_return_record(
            borrow_return_record,
            {
                "confirm_status": ConfirmStatus.CONFIRMED,
                "confirmed_status": confirm_in.confirmed_status,
                "confirm_remark": confirm_in.confirm_remark,
                "confirmer_id": admin_id,
                "confirm_time": confirm_time,
            },
            session,
        )
        borrow_record_crud.update_borrow_record(
            borrow_record,
            {"status": BorrowRecordStatus.COMPLETED},
            session,
        )
        change_equipment_status_service(
            session=session,
            equipment=equipment,
            target_status=target_equipment_status,
        )
        return BorrowReturnConfirmOut(
            borrow_record_id=borrow_record.id,
            borrow_record_status=borrow_record.status,
            return_record_id=borrow_return_record.id,
            confirm_status=borrow_return_record.confirm_status,
            confirmed_status=borrow_return_record.confirmed_status,
            confirm_remark=borrow_return_record.confirm_remark,
            confirm_time=borrow_return_record.confirm_time,
        )
