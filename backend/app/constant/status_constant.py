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


class ConfirmStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class RepairReportStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class RepairOrderStatus:
    PENDING_ASSIGN = "pending_assign"
    PENDING_REPAIR = "pending_repair"
    REPAIRING = "repairing"
    PENDING_CONFIRM = "pending_confirm"
    COMPLETED = "completed"
    UNREPAIRABLE = "unrepairable"
    SCRAPPED = "scrapped"


# 可选：生成状态映射字典，用于前端/数据库转换
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

# 可选：所有状态英文列表，用于参数校验
ITEM_STATUS_CODES = list(ITEM_STATUS_MAP.keys())
