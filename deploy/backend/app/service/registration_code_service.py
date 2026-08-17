from datetime import datetime

from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.exceptions import BussinessException
from app.crud import registration_code_crud
from app.db.models.registration_code_model import RegistrationCode
from app.schema.registration_code_schema import (
    RegistrationCodeCreate,
    RegistrationCodeOut,
    RegistrationCodeQuery,
    RegistrationCodeUpdate,
)


def query_registration_codes_service(session: Session, query: RegistrationCodeQuery) -> Page[RegistrationCodeOut]:
    # 按查询条件分页读取注册码，并转换为统一的分页响应模型。
    result = registration_code_crud.query_registration_codes(session, query)
    items = [RegistrationCodeOut.model_validate(item) for item in result.items]
    return Page(items=items, total=result.total, page=query.page, size=query.size, pages=result.pages)


def create_registration_code_service(session: Session, code_in: RegistrationCodeCreate) -> RegistrationCodeOut:
    with session.begin():
        # 注册码需要在管理端展示并供注册时精确查询，因此按明文存储。
        if registration_code_crud.get_registration_code_by_code(session, code_in.code):
            raise BussinessException("注册码已存在", status_code=409)
        code = RegistrationCode(code=code_in.code, code_type=code_in.code_type)
        # 在当前事务中新增注册码记录。
        registration_code_crud.add_registration_code(code, session)
    return RegistrationCodeOut.model_validate(code)


def update_registration_code_service(session: Session, code_id: int, code_in: RegistrationCodeUpdate) -> None:
    with session.begin():
        # 先确认待更新的注册码存在。
        code = registration_code_crud.get_registration_code_by_id(session, code_id)
        if not code:
            raise BussinessException("注册码不存在", status_code=404)
        # 仅更新请求中显式传入的字段；前端刷新时会传入 is_used=False 重置使用状态。
        values = code_in.model_dump(exclude_unset=True)
        if "code" in values:
            same_code = registration_code_crud.get_registration_code_by_code(session, values["code"])
            if same_code and same_code.id != code_id:
                raise BussinessException("注册码已存在", status_code=409)
        for field, value in values.items():
            setattr(code, field, value)
        code.update_time = datetime.now()


def delete_registration_code_service(session: Session, code_id: int) -> None:
    with session.begin():
        # 删除前确认目标注册码存在，避免静默删除不存在的数据。
        code = registration_code_crud.get_registration_code_by_id(session, code_id)
        if not code:
            raise BussinessException("注册码不存在", status_code=404)
        # 在当前事务中删除注册码记录。
        registration_code_crud.delete_registration_code(code, session)
