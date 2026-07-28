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

# 可选：生成状态映射字典，用于前端/数据库转换
ITEM_STATUS_MAP = {
    "available": ItemStatus.AVAILABLE,
    "pending_borrow": ItemStatus.PENDING_BORROW,
    "borrowed": ItemStatus.BORROWED,
    "pending_return": ItemStatus.PENDING_RETURN,
    "damaged": ItemStatus.DAMAGED,
    "repair_pending": ItemStatus.REPAIR_PENDING,
    "repairing": ItemStatus.REPAIRING,
    "repaired": ItemStatus.REPAIRED,
    "scrapped": ItemStatus.SCRAPPED,
    "offline": ItemStatus.OFFLINE,
}

# 可选：所有状态英文列表，用于参数校验
ITEM_STATUS_CODES = list(ITEM_STATUS_MAP.keys())