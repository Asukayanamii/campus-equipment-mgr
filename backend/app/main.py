from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger
from app.core.exception_handler import register_exception_handler
from app.core.exceptions import BussinessException
from app.result.result import Result

app = FastAPI(title="campus-equipment-mgr",description="校园设备管理系统",version="0.0.1")

register_exception_handler(app)

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
