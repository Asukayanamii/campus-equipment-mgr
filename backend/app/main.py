from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination, paginate

from app.api.common import common
from app.api.user import user, equipment, equipment_category, borrow_record, repair_report
from app.api.admin import admin, borrow_record as admin_borrow_record, equipment as admin_equipment, equipment_category as admin_equipment_category
from app.api.repair import repair, equipment as repair_equipment, equipment_category as repair_equipment_category
from app.core.exception_handler import register_exception_handler
from app.db import models
from app.db.session import Base, engine
from app.result.result import Result

app = FastAPI(title="campus-equipment-mgr",description="校园设备管理系统",version="0.0.1")


@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)

register_exception_handler(app)
add_pagination(app)  # 全局注册分页工具
app.include_router(user.router)
app.include_router(equipment.router)
app.include_router(equipment_category.router)
app.include_router(borrow_record.router)
app.include_router(repair_report.router)
app.include_router(admin.router)
app.include_router(admin_borrow_record.router)
app.include_router(admin_equipment.router)
app.include_router(admin_equipment_category.router)
app.include_router(repair.router)
app.include_router(repair_equipment.router)
app.include_router(repair_equipment_category.router)
app.include_router(common.router)

# 开发环境：允许所有源（仅用于开发！）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],         # 允许所有方法
    allow_headers=["*"],         # 允许所有请求头
)


@app.get("/")
async def root():
    return Result.success(message="基础相应格式，code=0表示成功，code=1表示业务逻辑出错失败",data={"name":"campus-equipment-mgr测试响应对象实例"})


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
