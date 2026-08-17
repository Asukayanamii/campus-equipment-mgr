from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models.operation_log_model import OperationLog
from app.schema.operation_log_schema import OperationLogQuery


def add_operation_log(operation_log: OperationLog, session: Session) -> None:
    """在当前事务中写入一条业务操作日志。"""
    session.add(operation_log)
    session.flush()


def query_operation_logs(session: Session, query: OperationLogQuery) -> Page[OperationLog]:
    """按业务对象、设备和操作者筛选操作日志。"""
    stmt = select(OperationLog)
    if query.business_type:
        stmt = stmt.where(OperationLog.business_type == query.business_type)
    if query.business_id:
        stmt = stmt.where(OperationLog.business_id == query.business_id)
    if query.equipment_id:
        stmt = stmt.where(OperationLog.equipment_id == query.equipment_id)
    if query.action:
        stmt = stmt.where(OperationLog.action == query.action)
    if query.operator_role:
        stmt = stmt.where(OperationLog.operator_role == query.operator_role)
    if query.operator_id:
        stmt = stmt.where(OperationLog.operator_id == query.operator_id)
    stmt = stmt.order_by(desc(OperationLog.create_time), desc(OperationLog.id))
    return paginate(session, stmt, query)


def query_operation_logs_by_business(
    session: Session,
    business_type: str,
    business_id: int,
) -> list[OperationLog]:
    """按业务对象读取按时间正序排列的完整操作历史。"""
    stmt = (
        select(OperationLog)
        .where(OperationLog.business_type == business_type, OperationLog.business_id == business_id)
        .order_by(OperationLog.create_time, OperationLog.id)
    )
    return list(session.scalars(stmt).all())
