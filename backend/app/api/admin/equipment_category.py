from fastapi import APIRouter, Depends, Path, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import admin_verity
from app.core.logger import logger
from app.db.session import get_db
from app.result.result import Result
from app.schema.equipment_category_schema import CategoryCreate, CategoryQuery, CategoryResp, CategoryUpdate
from app.service.equipment_category_service import (
    create_category_service,
    delete_category_service,
    get_category_service,
    query_categories_service,
    update_category_service,
)

router = APIRouter(
    prefix="/admin/equipment-category",
    tags=["管理端/设备分类相关"],
    dependencies=[Depends(admin_verity)],
)


@router.get("/page", response_model=Result[Page[CategoryResp]], name="分页条件查询设备分类")
def page_categories(query: CategoryQuery = Query(), db: Session = Depends(get_db)):
    logger.info("管理端分页条件查询设备分类")
    return Result.success(query_categories_service(db, query))


@router.get("/{categoryId}", response_model=Result[CategoryResp], name="根据 ID 查询设备分类")
def get_category(
    category_id: int = Path(..., alias="categoryId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端根据 ID 查询设备分类，分类 ID：%s", category_id)
    return Result.success(get_category_service(db, category_id))


@router.post("/", response_model=Result, name="新增设备分类")
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    logger.info("管理端新增设备分类，分类名称：%s", category_in.category_name)
    create_category_service(db, category_in)
    return Result.success()


@router.put("/{categoryId}", response_model=Result, name="根据 ID 更新设备分类")
def update_category(
    category_in: CategoryUpdate,
    category_id: int = Path(..., alias="categoryId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端根据 ID 更新设备分类，分类 ID：%s", category_id)
    update_category_service(db, category_id, category_in)
    return Result.success()


@router.delete("/{categoryId}", response_model=Result, name="根据 ID 删除设备分类")
def delete_category(
    category_id: int = Path(..., alias="categoryId", ge=1),
    db: Session = Depends(get_db),
):
    logger.info("管理端根据 ID 删除设备分类，分类 ID：%s", category_id)
    delete_category_service(db, category_id)
    return Result.success()
