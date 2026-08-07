# 设备物品借用全状态常量定义
class ItemStatus:
    # 可借用
    AVAILABLE = "可借用"
    # 借用审核中
    PENDING_BORROW = "借用审核中"
    # 已借出
    BORROWED = "已借出"
    # 待确认归还
    PENDING_RETURN = "待确认归还"
    # 已损坏
    DAMAGED = "已损坏"
    # 待维修
    REPAIR_PENDING = "待维修"
    # 维修中
    REPAIRING = "维修中"
    # 已维修
    REPAIRED = "已维修"
    # 已报废
    SCRAPPED = "已报废"
    # 已下架
    OFFLINE = "已下架"


class ItemStatusCode:
    AVAILABLE = "available"
    PENDING_BORROW = "pending_borrow"
    BORROWED = "borrowed"
    PENDING_RETURN = "pending_return"
    DAMAGED = "damaged"
    REPAIR_PENDING = "repair_pending"
    REPAIRING = "repairing"
    REPAIRED = "repaired"
    SCRAPPED = "scrapped"
    OFFLINE = "offline"

# 生成状态映射字典，用于前端/数据库转换
ITEM_STATUS_MAP = {
    ItemStatusCode.AVAILABLE: ItemStatus.AVAILABLE,
    ItemStatusCode.PENDING_BORROW: ItemStatus.PENDING_BORROW,
    ItemStatusCode.BORROWED: ItemStatus.BORROWED,
    ItemStatusCode.PENDING_RETURN: ItemStatus.PENDING_RETURN,
    ItemStatusCode.DAMAGED: ItemStatus.DAMAGED,
    ItemStatusCode.REPAIR_PENDING: ItemStatus.REPAIR_PENDING,
    ItemStatusCode.REPAIRING: ItemStatus.REPAIRING,
    ItemStatusCode.REPAIRED: ItemStatus.REPAIRED,
    ItemStatusCode.SCRAPPED: ItemStatus.SCRAPPED,
    ItemStatusCode.OFFLINE: ItemStatus.OFFLINE,
}

class BorrowRecordStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BORROWED = "borrowed"
    PENDING_RETURN = "pending_return"
    COMPLETED = "completed"


BORROW_RECORD_STATUS_MAP = {
    BorrowRecordStatus.PENDING: "待审核",
    BorrowRecordStatus.APPROVED: "审核通过",
    BorrowRecordStatus.REJECTED: "审核驳回",
    BorrowRecordStatus.BORROWED: "已借出",
    BorrowRecordStatus.PENDING_RETURN: "待确认归还",
    BorrowRecordStatus.COMPLETED: "已完成",
}

BORROW_RECORD_STATUS_CODES = list(BORROW_RECORD_STATUS_MAP.keys())


class BorrowReturnStatus:
    NORMAL = "normal"
    DAMAGED = "damaged"


BORROW_RETURN_STATUS_MAP = {
    BorrowReturnStatus.NORMAL: "正常",
    BorrowReturnStatus.DAMAGED: "损坏",
}

BORROW_RETURN_STATUS_CODES = list(BORROW_RETURN_STATUS_MAP.keys())


class ConfirmStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


CONFIRM_STATUS_MAP = {
    ConfirmStatus.PENDING: "待确认",
    ConfirmStatus.CONFIRMED: "已确认",
    ConfirmStatus.REJECTED: "已驳回",
}

CONFIRM_STATUS_CODES = list(CONFIRM_STATUS_MAP.keys())


class RepairReportStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


REPAIR_REPORT_STATUS_MAP = {
    RepairReportStatus.PENDING: "待处理",
    RepairReportStatus.CONFIRMED: "已确认",
    RepairReportStatus.REJECTED: "已驳回",
}

REPAIR_REPORT_STATUS_CODES = list(REPAIR_REPORT_STATUS_MAP.keys())


class RepairOrderStatus:
    PENDING_ASSIGN = "pending_assign"
    PENDING_REPAIR = "pending_repair"
    REPAIRING = "repairing"
    PENDING_CONFIRM = "pending_confirm"
    COMPLETED = "completed"
    UNREPAIRABLE = "unrepairable"
    SCRAPPED = "scrapped"
    CANCELLED = "cancelled"


REPAIR_ORDER_STATUS_MAP = {
    RepairOrderStatus.PENDING_ASSIGN: "待派单",
    RepairOrderStatus.PENDING_REPAIR: "待维修",
    RepairOrderStatus.REPAIRING: "维修中",
    RepairOrderStatus.PENDING_CONFIRM: "待确认",
    RepairOrderStatus.COMPLETED: "已完成",
    RepairOrderStatus.UNREPAIRABLE: "无法维修",
    RepairOrderStatus.SCRAPPED: "已报废",
    RepairOrderStatus.CANCELLED: "已取消",
}

REPAIR_ORDER_STATUS_CODES = list(REPAIR_ORDER_STATUS_MAP.keys())


class AuditBusinessType:
    BORROW_RECORD = "borrow_record"
    EQUIPMENT = "equipment"


AUDIT_BUSINESS_TYPE_MAP = {
    AuditBusinessType.BORROW_RECORD: "借用记录",
    AuditBusinessType.EQUIPMENT: "设备",
}

AUDIT_BUSINESS_TYPE_CODES = list(AUDIT_BUSINESS_TYPE_MAP.keys())


class AuditOperationType:
    REVIEW = "review"
    CONFIRM_RETURN = "confirm_return"


AUDIT_OPERATION_TYPE_MAP = {
    AuditOperationType.REVIEW: "审核借用申请",
    AuditOperationType.CONFIRM_RETURN: "确认设备归还",
}

AUDIT_OPERATION_TYPE_CODES = list(AUDIT_OPERATION_TYPE_MAP.keys())



# 可选：所有状态英文列表，用于参数校验
ITEM_STATUS_CODES = list(ITEM_STATUS_MAP.keys())
