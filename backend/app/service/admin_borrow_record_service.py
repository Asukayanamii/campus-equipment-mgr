from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import (
    BorrowRecordStatus,
    ItemStatusCode,
    OperationAction,
    OperationActorRole,
    OperationBusinessType,
)
from app.core.exceptions import BussinessException
from app.crud import borrow_record_crud, borrow_return_image_crud, equipment_crud
from app.schema.admin_borrow_record_schema import (
    AdminBorrowRecordOut,
    AdminBorrowRecordPageOut,
    AdminBorrowRecordQuery,
    BorrowRecordReview,
    BorrowRecordReviewOut,
)
from app.service.equipment_service import change_equipment_status_service
from app.service.operation_log_service import create_operation_log


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

    # 补充学生归还申报和损坏图片信息。
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
        # 审核结论与设备可用状态同步记录，保留审核人和审核备注。
        operation_action = OperationAction.BORROW_APPROVE if review_in.approved else OperationAction.BORROW_REJECT
        create_operation_log(
            session,
            OperationBusinessType.BORROW_RECORD,
            borrow_record.id,
            operation_action,
            OperationActorRole.ADMIN,
            admin_id,
            equipment_id=equipment.id,
            from_status=BorrowRecordStatus.PENDING,
            to_status=result_status,
            remark=review_in.review_remark,
        )
        create_operation_log(
            session,
            OperationBusinessType.EQUIPMENT,
            equipment.id,
            operation_action,
            OperationActorRole.ADMIN,
            admin_id,
            equipment_id=equipment.id,
            from_status=ItemStatusCode.PENDING_BORROW,
            to_status=equipment_status,
            remark=review_in.review_remark,
        )
        return BorrowRecordReviewOut.model_validate(borrow_record)
