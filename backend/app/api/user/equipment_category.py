from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import user_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_category_schema import CategoryQuery, CategoryResp
from app.service.equipment_category_service import query_categories_service


router = APIRouter(
    prefix="/user/equipment-category",
    tags=["学生端/设备分类相关"],
    dependencies=[Depends(user_verity)],
)


@router.get("/page", response_model=Result[Page[CategoryResp]], name="分页条件查询设备分类")
def page_categories(query: CategoryQuery = Query(), db: Session = Depends(get_db)):
    logger.info("学生端分页条件查询设备分类")
    return Result.success(query_categories_service(db, query))
