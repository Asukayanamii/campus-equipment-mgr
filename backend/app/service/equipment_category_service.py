from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.exceptions import BussinessException
from app.crud import equipment_category_crud
from app.db.models.equipment_category_model import EquipmentCategory
from app.schema.equipment_category_schema import CategoryCreate, CategoryQuery, CategoryResp, CategoryUpdate


def query_categories_service(session: Session, query: CategoryQuery) -> Page[CategoryResp]:
    # 执行分类分页查询并转换响应模型。
    result = equipment_category_crud.query_categories(session, query)
    items = [CategoryResp.model_validate(category) for category in result.items]
    return Page(items=items, total=result.total, page=query.page, size=result.size, pages=result.pages)


def get_category_service(session: Session, category_id: int) -> CategoryResp:
    # 查询未删除分类，缺失时返回业务异常。
    category = equipment_category_crud.get_category_by_id(session, category_id)
    if not category:
        raise BussinessException("设备分类不存在", status_code=404)
    return CategoryResp.model_validate(category)


def create_category_service(session: Session, category_in: CategoryCreate) -> None:
    with session.begin():
        # 校验分类名称唯一后创建分类。
        if equipment_category_crud.get_category_by_name(session, category_in.category_name):
            raise BussinessException("设备分类名称已存在", status_code=409)
        equipment_category_crud.add_category(EquipmentCategory(**category_in.model_dump()), session)


def update_category_service(session: Session, category_id: int, category_in: CategoryUpdate) -> None:
    with session.begin():
        # 确认目标分类存在且未被逻辑删除。
        category = equipment_category_crud.get_category_by_id(session, category_id)
        if not category:
            raise BussinessException("设备分类不存在", status_code=404)

        # 仅提取请求中显式传入的更新字段。
        values = category_in.model_dump(exclude_unset=True)
        category_name = values.get("category_name")
        if category_name:
            same_name_category = equipment_category_crud.get_category_by_name(session, category_name)
            if same_name_category and same_name_category.id != category_id:
                raise BussinessException("设备分类名称已存在", status_code=409)
        # 校验新分类名称后写入变更。
        equipment_category_crud.update_category(category, values, session)


def delete_category_service(session: Session, category_id: int) -> None:
    with session.begin():
        # 确认分类存在后执行逻辑删除。
        category = equipment_category_crud.get_category_by_id(session, category_id)
        if not category:
            raise BussinessException("设备分类不存在", status_code=404)
        equipment_category_crud.delete_category(category, session)
