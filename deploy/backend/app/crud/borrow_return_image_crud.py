from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.db.models.borrow_return_image_model import BorrowReturnImage


def add_borrow_return_image(borrow_return_image: BorrowReturnImage, session: Session) -> None:
    session.add(borrow_return_image)
    session.flush()


def get_borrow_return_images_by_return_record_id(
    session: Session,
    return_record_id: int,
) -> list[BorrowReturnImage]:
    stmt = (
        select(BorrowReturnImage)
        .where(BorrowReturnImage.return_record_id == return_record_id)
        .order_by(asc(BorrowReturnImage.sort), asc(BorrowReturnImage.id))
    )
    return session.scalars(stmt).all()
