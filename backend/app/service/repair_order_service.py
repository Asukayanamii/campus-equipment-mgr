from datetime import datetime

from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import ITEM_STATUS_MAP, ItemStatusCode, RepairOrderStatus, RepairReportStatus
from app.core.exceptions import BussinessException
from app.crud import borrow_return_image_crud, equipment_crud, repair_order_crud, repair_report_crud, repair_user_crud
from app.db.models.repair_order_image_model import RepairOrderImage
from app.schema.common_schema import PageQuery
from app.schema.repair_order_schema import (
    RepairOrderActionOut,
    RepairOrderAssignIn,
    RepairOrderAssignOut,
    RepairOrderCompletionIn,
    RepairOrderCompletionOut,
    RepairOrderOut,
    RepairOrderPageOut,
    RepairOrderQuery,
    RepairReportAdminOut,
    RepairReportAdminPageOut,
    RepairReportConfirmOut,
    RepairUserPageOut,
)


def _get_image_urls(session: Session, order_id: int) -> tuple[list[str], list[str]]:
    images = repair_order_crud.get_repair_order_images(session, order_id)
    return (
        [image.image_url for image in images if image.image_type == "before"],
        [image.image_url for image in images if image.image_type == "after"],
    )


def _build_order_detail(session: Session, detail) -> RepairOrderOut:
    order, report, equipment, user, repair_user = detail
    result = RepairOrderOut.model_validate(order)
    result.user_id = report.user_id if report else None
    result.user_name = user.name if user else None
    result.damage_description = report.damage_description if report else None
    result.equipment_id = order.equipment_id
    if equipment:
        result.equipment_no = equipment.equipment_no
        result.equipment_name = equipment.equipment_name
        result.equipment_status = ITEM_STATUS_MAP.get(equipment.status, equipment.status)
    if repair_user:
        result.repair_user_id = repair_user.id
        result.repair_user_name = repair_user.name
    result.damage_images = (
        [image.image_url for image in borrow_return_image_crud.get_borrow_return_images_by_return_record_id(session, report.return_record_id)]
        if report else []
    )
    result.before_images, result.after_images = _get_image_urls(session, order.id)
    return result


def query_repair_orders_service(
    session: Session,
    query: RepairOrderQuery,
    repair_user_id: int | None = None,
) -> Page[RepairOrderPageOut]:
    result = []
    page = repair_order_crud.query_repair_orders(session, query, repair_user_id)
    for order, equipment, repair_user in page.items:
        item = RepairOrderPageOut.model_validate(order)
        item.equipment_name = equipment.equipment_name if equipment else None
        item.repair_user_name = repair_user.name if repair_user else None
        result.append(item)
    return Page(items=result, total=page.total, page=page.page, size=page.size, pages=page.pages)


def get_repair_order_service(
    session: Session,
    repair_order_id: int,
    repair_user_id: int | None = None,
) -> RepairOrderOut:
    detail = repair_order_crud.get_repair_order_detail(session, repair_order_id)
    if not detail or (repair_user_id is not None and detail[0].repair_user_id != repair_user_id):
        raise BussinessException("维修工单不存在", status_code=404)
    return _build_order_detail(session, detail)


def query_repair_users_service(session: Session, query: PageQuery) -> Page[RepairUserPageOut]:
    page = repair_user_crud.query_repair_users(session, query)
    items = [RepairUserPageOut.model_validate(item) for item in page.items]
    return Page(items=items, total=page.total, page=page.page, size=page.size, pages=page.pages)


def query_repair_reports_by_admin_service(session: Session, query) -> Page[RepairReportAdminPageOut]:
    page = repair_report_crud.query_repair_reports_by_admin(session, query)
    items = []
    for report, user, equipment, order in page.items:
        item = RepairReportAdminPageOut.model_validate(report)
        item.user_name = user.name if user else None
        item.equipment_name = equipment.equipment_name if equipment else None
        item.repair_order_id = order.id if order else None
        item.repair_order_status = order.status if order else None
        items.append(item)
    return Page(items=items, total=page.total, page=page.page, size=page.size, pages=page.pages)


def get_repair_report_by_admin_service(session: Session, repair_report_id: int) -> RepairReportAdminOut:
    detail = repair_report_crud.get_repair_report_detail_by_id(session, repair_report_id)
    if not detail:
        raise BussinessException("报修记录不存在", status_code=404)
    report, user, equipment, order = detail
    result = RepairReportAdminOut.model_validate(report)
    result.user_name = user.name if user else None
    result.username = user.username if user else None
    if equipment:
        result.equipment_no = equipment.equipment_no
        result.equipment_name = equipment.equipment_name
    result.damage_images = [
        image.image_url
        for image in borrow_return_image_crud.get_borrow_return_images_by_return_record_id(
            session,
            report.return_record_id,
        )
    ]
    if order:
        result.repair_order_id = order.id
        result.repair_order_status = order.status
    return result


def confirm_repair_report_service(session: Session, repair_report_id: int) -> RepairReportConfirmOut:
    with session.begin():
        report = repair_report_crud.get_repair_report_by_id_for_update(session, repair_report_id)
        if not report:
            raise BussinessException("报修记录不存在", status_code=404)
        if report.status != RepairReportStatus.PENDING:
            raise BussinessException("当前报修记录不能确认", status_code=400)
        repair_report_crud.update_repair_report(
            report,
            {"status": RepairReportStatus.CONFIRMED},
            session,
        )
        return RepairReportConfirmOut.model_validate(report)


def _get_owned_order_for_update(session: Session, repair_order_id: int, repair_user_id: int):
    order = repair_order_crud.get_repair_order_by_id_for_update(session, repair_order_id)
    if not order or order.repair_user_id != repair_user_id:
        raise BussinessException("维修工单不存在", status_code=404)
    return order


def assign_repair_order_service(
    session: Session,
    repair_order_id: int,
    assign_in: RepairOrderAssignIn,
) -> RepairOrderAssignOut:
    with session.begin():
        order = repair_order_crud.get_repair_order_by_id_for_update(session, repair_order_id)
        if not order:
            raise BussinessException("维修工单不存在", status_code=404)
        if order.status != RepairOrderStatus.PENDING_ASSIGN:
            raise BussinessException("当前工单不能派单", status_code=400)
        report = repair_report_crud.get_repair_report_by_id_for_update(session, order.repair_report_id)
        if not report or report.status != RepairReportStatus.CONFIRMED:
            raise BussinessException("报修记录尚未确认", status_code=400)
        repair_user = repair_user_crud.get_repair_user_by_id(assign_in.repair_user_id, session)
        if not repair_user:
            raise BussinessException("维修人员不存在", status_code=404)
        now = datetime.now()
        repair_order_crud.update_repair_order(
            order,
            {
                "repair_user_id": repair_user.id,
                "status": RepairOrderStatus.PENDING_ACCEPT,
                "assign_remark": assign_in.assign_remark,
                "assign_time": now,
            },
            session,
        )
        result = RepairOrderAssignOut.model_validate(order)
        result.equipment_status = None
        return result


def accept_repair_order_service(session: Session, repair_order_id: int, repair_user_id: int) -> RepairOrderActionOut:
    with session.begin():
        order = _get_owned_order_for_update(session, repair_order_id, repair_user_id)
        if order.status != RepairOrderStatus.PENDING_ACCEPT:
            raise BussinessException("当前工单不能接单", status_code=400)
        repair_order_crud.update_repair_order(order, {"status": RepairOrderStatus.PENDING_REPAIR}, session)
        return RepairOrderActionOut.model_validate(order)


def start_repair_order_service(session: Session, repair_order_id: int, repair_user_id: int) -> RepairOrderActionOut:
    with session.begin():
        order = _get_owned_order_for_update(session, repair_order_id, repair_user_id)
        if order.status != RepairOrderStatus.PENDING_REPAIR:
            raise BussinessException("当前工单不能开始维修", status_code=400)
        equipment = equipment_crud.get_equipment_by_id_for_update(session, order.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)
        repair_order_crud.update_repair_order(order, {"status": RepairOrderStatus.REPAIRING}, session)
        equipment.status = ItemStatusCode.REPAIRING
        session.flush()
        result = RepairOrderActionOut.model_validate(order)
        result.equipment_status = ITEM_STATUS_MAP.get(equipment.status, equipment.status)
        return result


def complete_repair_order_service(
    session: Session,
    repair_order_id: int,
    repair_user_id: int,
    completion_in: RepairOrderCompletionIn,
) -> RepairOrderCompletionOut:
    with session.begin():
        order = _get_owned_order_for_update(session, repair_order_id, repair_user_id)
        if order.status != RepairOrderStatus.REPAIRING:
            raise BussinessException("当前工单不能提交维修结果", status_code=400)
        equipment = equipment_crud.get_equipment_by_id_for_update(session, order.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)
        target_order_status = (
            RepairOrderStatus.PENDING_CONFIRM
            if completion_in.result_status == "repaired"
            else RepairOrderStatus.UNREPAIRABLE
        )
        target_equipment_status = (
            ItemStatusCode.REPAIRED
            if completion_in.result_status == "repaired"
            else ItemStatusCode.DAMAGED
        )
        repair_order_crud.update_repair_order(
            order,
            {
                "status": target_order_status,
                "fault_cause": completion_in.fault_cause,
                "repair_process": completion_in.repair_process,
                "repair_result": completion_in.repair_result,
                "completion_time": datetime.now(),
            },
            session,
        )
        for image_type, image_urls in (("before", completion_in.before_images), ("after", completion_in.after_images)):
            for sort, image_url in enumerate(image_urls):
                repair_order_crud.add_repair_order_image(
                    RepairOrderImage(
                        repair_order_id=order.id,
                        image_type=image_type,
                        image_url=image_url,
                        sort=sort,
                    ),
                    session,
                )
        equipment.status = target_equipment_status
        session.flush()
        result = RepairOrderCompletionOut.model_validate(order)
        result.equipment_status = ITEM_STATUS_MAP.get(equipment.status, equipment.status)
        result.before_images = completion_in.before_images
        result.after_images = completion_in.after_images
        return result


def confirm_completed_repair_order_service(session: Session, repair_order_id: int) -> RepairOrderActionOut:
    with session.begin():
        order = repair_order_crud.get_repair_order_by_id_for_update(session, repair_order_id)
        if not order:
            raise BussinessException("维修工单不存在", status_code=404)
        if order.status != RepairOrderStatus.PENDING_CONFIRM:
            raise BussinessException("当前工单不能确认完成", status_code=400)
        equipment = equipment_crud.get_equipment_by_id_for_update(session, order.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)
        repair_order_crud.update_repair_order(order, {"status": RepairOrderStatus.COMPLETED}, session)
        equipment.status = ItemStatusCode.AVAILABLE
        session.flush()
        result = RepairOrderActionOut.model_validate(order)
        result.equipment_status = ITEM_STATUS_MAP.get(equipment.status, equipment.status)
        return result


def scrap_repair_order_service(session: Session, repair_order_id: int) -> RepairOrderActionOut:
    with session.begin():
        order = repair_order_crud.get_repair_order_by_id_for_update(session, repair_order_id)
        if not order:
            raise BussinessException("维修工单不存在", status_code=404)
        if order.status != RepairOrderStatus.UNREPAIRABLE:
            raise BussinessException("当前工单不能报废", status_code=400)
        equipment = equipment_crud.get_equipment_by_id_for_update(session, order.equipment_id)
        if not equipment:
            raise BussinessException("设备不存在", status_code=404)
        repair_order_crud.update_repair_order(order, {"status": RepairOrderStatus.SCRAPPED}, session)
        equipment.status = ItemStatusCode.SCRAPPED
        session.flush()
        result = RepairOrderActionOut.model_validate(order)
        result.equipment_status = ITEM_STATUS_MAP.get(equipment.status, equipment.status)
        return result
