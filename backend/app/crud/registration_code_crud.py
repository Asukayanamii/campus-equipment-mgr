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
    return paginate(session, stmt, query)


def get_registration_code_by_id(session: Session, code_id: int) -> RegistrationCode | None:
    return session.scalar(select(RegistrationCode).where(RegistrationCode.id == code_id))


def get_unused_registration_code_by_code(session: Session, code: str) -> RegistrationCode | None:
    stmt = select(RegistrationCode).where(
        RegistrationCode.code == code,
        RegistrationCode.is_used.is_(False),
    )
    return session.scalar(stmt)


def get_registration_code_by_code(session: Session, code: str) -> RegistrationCode | None:
    return session.scalar(select(RegistrationCode).where(RegistrationCode.code == code))


def add_registration_code(code: RegistrationCode, session: Session) -> None:
    session.add(code)
    session.flush()


def delete_registration_code(code: RegistrationCode, session: Session) -> None:
    session.delete(code)
    session.flush()
