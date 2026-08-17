from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.constant.status_constant import OperationBusinessType
from app.core.exceptions import BussinessException
from app.crud import operation_log_crud, repair_order_crud
from app.db.models.operation_log_model import OperationLog
from app.schema.operation_log_schema import OperationLogOut, OperationLogQuery


def create_operation_log(
    session: Session,
    business_type: str,
    business_id: int,
    action: str,
    operator_role: str,
    operator_id: int | None,
    equipment_id: int | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    remark: str | None = None,
) -> None:
    """在业务事务内记录操作人、动作和前后状态。"""
    operation_log_crud.add_operation_log(
        OperationLog(
            business_type=business_type,
            business_id=business_id,
            equipment_id=equipment_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            operator_role=operator_role,
            operator_id=operator_id,
            remark=remark,
        ),
        session,
    )


def query_operation_logs_service(session: Session, query: OperationLogQuery) -> Page[OperationLogOut]:
    """分页查询全量操作日志，供管理员审计使用。"""
    page = operation_log_crud.query_operation_logs(session, query)
    items = [OperationLogOut.model_validate(item) for item in page.items]
    return Page(items=items, total=page.total, page=page.page, size=page.size, pages=page.pages)


def query_repair_order_operation_logs_service(
    session: Session,
    repair_order_id: int,
    repair_user_id: int,
) -> list[OperationLogOut]:
    """维修人员只能查看分配给自己的工单操作历史。"""
    detail = repair_order_crud.get_repair_order_detail(session, repair_order_id)
    if not detail or detail[0].repair_user_id != repair_user_id:
        raise BussinessException("维修工单不存在", status_code=404)
    logs = operation_log_crud.query_operation_logs_by_business(
        session,
        OperationBusinessType.REPAIR_ORDER,
        repair_order_id,
    )
    return [OperationLogOut.model_validate(item) for item in logs]
