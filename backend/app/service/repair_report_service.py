from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.exceptions import BussinessException
from app.crud import borrow_return_image_crud, repair_report_crud
from app.schema.repair_report_schema import RepairReportOut, RepairReportPageOut, RepairReportQuery


def query_repair_report_by_user_service(
    session: Session,
    user_id: int,
    query: RepairReportQuery,
) -> Page[RepairReportPageOut]:
    list = []
    # 按当前学生 ID 查询报修记录及列表展示所需的设备名称。
    res = repair_report_crud.query_repair_report_by_user(session, user_id, query)
    for repair_report, equipment in res.items:
        repair_report_out = RepairReportPageOut.model_validate(repair_report)
        repair_report_out.equipment_name = equipment.equipment_name if equipment else None
        list.append(repair_report_out)
    # 保留分页器元数据并返回精简列表模型。
    return Page(items=list, total=res.total, page=query.page, size=res.size, pages=res.pages)


def get_repair_report_detail_by_user_service(
    session: Session,
    repair_report_id: int,
    user_id: int,
) -> RepairReportOut:
    # 查询时同时按报修记录 ID 和当前学生 ID 过滤，隔离他人数据。
    repair_report_detail = repair_report_crud.get_repair_report_detail_by_id_and_user(
        session,
        repair_report_id,
        user_id,
    )
    if not repair_report_detail:
        raise BussinessException("报修记录不存在", status_code=404)

    # 组装报修详情，并读取归还记录下按顺序保存的损坏图片。
    repair_report, equipment, category, repair_order = repair_report_detail
    repair_report_out = RepairReportOut.model_validate(repair_report)
    repair_report_out.damage_images = [
        image.image_url
        for image in borrow_return_image_crud.get_borrow_return_images_by_return_record_id(
            session,
            repair_report.return_record_id,
        )
    ]
    # 补齐详情展示所需的设备和分类字段。
    if equipment:
        repair_report_out.equipment_no = equipment.equipment_no
        repair_report_out.equipment_name = equipment.equipment_name
        repair_report_out.category_id = equipment.category_id
        repair_report_out.category_name = category.category_name if category else None
        repair_report_out.spec = equipment.spec
        repair_report_out.brand = equipment.brand
        repair_report_out.unit = equipment.unit
        repair_report_out.location = equipment.location
        repair_report_out.purchase_date = equipment.purchase_date
        repair_report_out.price = equipment.price
        repair_report_out.cover_img = equipment.cover_img
        repair_report_out.equipment_status = equipment.status
        repair_report_out.remark = equipment.remark
    # 有关联工单时补充维修人员、派单和维修进度字段。
    if repair_order:
        repair_report_out.repair_order_id = repair_order.id
        repair_report_out.repair_user_id = repair_order.repair_user_id
        repair_report_out.repair_status = repair_order.status
        repair_report_out.assign_remark = repair_order.assign_remark
        repair_report_out.assign_time = repair_order.assign_time
        repair_report_out.fault_cause = repair_order.fault_cause
        repair_report_out.repair_process = repair_order.repair_process
        repair_report_out.repair_result = repair_order.repair_result
        repair_report_out.completion_time = repair_order.completion_time
    return repair_report_out
