# 设备物品借用全状态常量定义
class ItemStatus:
    # 可借用
    AVAILABLE = "可借用"
    # 借用审核中
    PENDING_BORROW = "借用审核中"
    # 已借出
    BORROWED = "已借出"
    # 待确认归还（预留扩展状态）
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
    COMPLETED = "completed"


BORROW_RECORD_STATUS_MAP = {
    BorrowRecordStatus.PENDING: "待审核",
    BorrowRecordStatus.APPROVED: "审核通过",
    BorrowRecordStatus.REJECTED: "审核驳回",
    BorrowRecordStatus.BORROWED: "已借出",
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
    PENDING_ACCEPT = "pending_accept"
    PENDING_REPAIR = "pending_repair"
    REPAIRING = "repairing"
    PENDING_CONFIRM = "pending_confirm"
    COMPLETED = "completed"
    UNREPAIRABLE = "unrepairable"
    SCRAPPED = "scrapped"
    CANCELLED = "cancelled"


REPAIR_ORDER_STATUS_MAP = {
    RepairOrderStatus.PENDING_ASSIGN: "待派单",
    RepairOrderStatus.PENDING_ACCEPT: "待接单",
    RepairOrderStatus.PENDING_REPAIR: "待维修",
    RepairOrderStatus.REPAIRING: "维修中",
    RepairOrderStatus.PENDING_CONFIRM: "待确认",
    RepairOrderStatus.COMPLETED: "已完成",
    RepairOrderStatus.UNREPAIRABLE: "无法维修",
    RepairOrderStatus.SCRAPPED: "已报废",
    RepairOrderStatus.CANCELLED: "已取消",
}

REPAIR_ORDER_STATUS_CODES = list(REPAIR_ORDER_STATUS_MAP.keys())


class OperationBusinessType:
    """操作日志关联的业务类型。"""

    BORROW_RECORD = "borrow_record"
    REPAIR_REPORT = "repair_report"
    REPAIR_ORDER = "repair_order"
    EQUIPMENT = "equipment"


OPERATION_BUSINESS_TYPE_MAP = {
    OperationBusinessType.BORROW_RECORD: "借用记录",
    OperationBusinessType.REPAIR_REPORT: "报修记录",
    OperationBusinessType.REPAIR_ORDER: "维修工单",
    OperationBusinessType.EQUIPMENT: "设备",
}

OPERATION_BUSINESS_TYPE_CODES = list(OPERATION_BUSINESS_TYPE_MAP.keys())


class OperationActorRole:
    """操作日志中的操作者角色。"""

    USER = "user"
    ADMIN = "admin"
    REPAIR_USER = "repair_user"
    SYSTEM = "system"


OPERATION_ACTOR_ROLE_MAP = {
    OperationActorRole.USER: "学生",
    OperationActorRole.ADMIN: "管理员",
    OperationActorRole.REPAIR_USER: "维修人员",
    OperationActorRole.SYSTEM: "系统",
}

OPERATION_ACTOR_ROLE_CODES = list(OPERATION_ACTOR_ROLE_MAP.keys())


class OperationAction:
    """操作日志动作编码。"""

    BORROW_APPLY = "borrow_apply"
    BORROW_APPROVE = "borrow_approve"
    BORROW_REJECT = "borrow_reject"
    BORROW_RETURN_NORMAL = "borrow_return_normal"
    BORROW_RETURN_DAMAGED = "borrow_return_damaged"
    REPAIR_REPORT_CREATE = "repair_report_create"
    REPAIR_REPORT_CONFIRM = "repair_report_confirm"
    REPAIR_ORDER_CREATE = "repair_order_create"
    REPAIR_ORDER_ASSIGN = "repair_order_assign"
    REPAIR_ORDER_ACCEPT = "repair_order_accept"
    REPAIR_ORDER_START = "repair_order_start"
    REPAIR_ORDER_COMPLETE = "repair_order_complete"
    REPAIR_ORDER_UNREPAIRABLE = "repair_order_unrepairable"
    REPAIR_ORDER_CONFIRM = "repair_order_confirm"
    REPAIR_ORDER_SCRAP = "repair_order_scrap"
    EQUIPMENT_CREATE = "equipment_create"
    EQUIPMENT_STATUS_CHANGE = "equipment_status_change"
    EQUIPMENT_DELETE = "equipment_delete"


OPERATION_ACTION_MAP = {
    OperationAction.BORROW_APPLY: "提交借用申请",
    OperationAction.BORROW_APPROVE: "审核借用通过",
    OperationAction.BORROW_REJECT: "审核借用驳回",
    OperationAction.BORROW_RETURN_NORMAL: "正常归还设备",
    OperationAction.BORROW_RETURN_DAMAGED: "损坏归还设备",
    OperationAction.REPAIR_REPORT_CREATE: "创建报修记录",
    OperationAction.REPAIR_REPORT_CONFIRM: "确认报修记录",
    OperationAction.REPAIR_ORDER_CREATE: "创建维修工单",
    OperationAction.REPAIR_ORDER_ASSIGN: "派发维修工单",
    OperationAction.REPAIR_ORDER_ACCEPT: "接收维修工单",
    OperationAction.REPAIR_ORDER_START: "开始维修",
    OperationAction.REPAIR_ORDER_COMPLETE: "提交维修完成",
    OperationAction.REPAIR_ORDER_UNREPAIRABLE: "提交无法维修结果",
    OperationAction.REPAIR_ORDER_CONFIRM: "确认维修完成",
    OperationAction.REPAIR_ORDER_SCRAP: "报废设备",
    OperationAction.EQUIPMENT_CREATE: "新增设备",
    OperationAction.EQUIPMENT_STATUS_CHANGE: "变更设备状态",
    OperationAction.EQUIPMENT_DELETE: "下架设备",
}

OPERATION_ACTION_CODES = list(OPERATION_ACTION_MAP.keys())


# 可选：所有状态英文列表，用于参数校验
ITEM_STATUS_CODES = list(ITEM_STATUS_MAP.keys())
