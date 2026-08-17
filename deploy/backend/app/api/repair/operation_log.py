from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.auth import repair_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.operation_log_schema import OperationLogOut
from app.service.operation_log_service import query_repair_order_operation_logs_service

router = APIRouter(
    prefix="/repair/orders",
    tags=["维修端/操作日志相关"],
    dependencies=[Depends(repair_verity)],
)


@router.get("/{repairOrderId}/operation-logs", response_model=Result[list[OperationLogOut]], name="查看本人维修工单操作历史")
def get_repair_order_operation_logs(
    repair_order_id: int = Path(..., alias="repairOrderId", ge=1),
    info: dict = Depends(repair_verity),
    db: Session = Depends(get_db),
):
    # 维修人员仅能查看当前已分配工单的审核和状态变更记录。
    logger.info("维修端查看工单操作历史，工单 ID：%s", repair_order_id)
    return Result.success(query_repair_order_operation_logs_service(db, repair_order_id, info["id"]))
