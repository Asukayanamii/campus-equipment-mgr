from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.registration_code_model import RegistrationCode
from app.schema.registration_code_schema import RegistrationCodeQuery


def query_registration_codes(session: Session, query: RegistrationCodeQuery) -> Page[RegistrationCode]:
    stmt = select(RegistrationCode).order_by(RegistrationCode.id.desc())
    if query.is_used is not None:
        stmt = stmt.where(RegistrationCode.is_used == query.is_used)
    if query.code_type is not None:
        stmt = stmt.where(RegistrationCode.code_type == query.code_type)
    return paginate(session, stmt, query)


def get_registration_code_by_id(session: Session, code_id: int) -> RegistrationCode | None:
    return session.scalar(select(RegistrationCode).where(RegistrationCode.id == code_id))


def get_unused_registration_code_by_code(session: Session, code: str, code_type: str) -> RegistrationCode | None:
    # 注册流程会在当前事务内立即占用注册码，使用行锁防止并发请求重复使用同一条记录。
    stmt = select(RegistrationCode).where(
        RegistrationCode.code == code,
        RegistrationCode.code_type == code_type,
        RegistrationCode.is_used.is_(False),
    ).with_for_update()
    return session.scalar(stmt)


def get_registration_code_by_code(session: Session, code: str) -> RegistrationCode | None:
    return session.scalar(select(RegistrationCode).where(RegistrationCode.code == code))


def add_registration_code(code: RegistrationCode, session: Session) -> None:
    session.add(code)
    session.flush()


def delete_registration_code(code: RegistrationCode, session: Session) -> None:
    session.delete(code)
    session.flush()
