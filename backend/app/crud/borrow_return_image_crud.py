from sqlalchemy.orm import Session

from app.db.models.borrow_return_image_model import BorrowReturnImage


def add_borrow_return_image(borrow_return_image: BorrowReturnImage, session: Session) -> None:
    session.add(borrow_return_image)
    session.flush()
