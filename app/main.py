"""FastAPI 主应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import database
from app.routers import user_router
from app.exceptions import BusinessException, ErrorCode
from app.utils.session import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    await database.connect()
    await init_redis()
    print(f"数据库连接成功: {settings.database_url}")
    print(f"Redis 连接成功: {settings.redis_url}")

    yield

    # 关闭时执行
    await database.disconnect()
    await close_redis()
    print("应用已关闭")


app = FastAPI(
    title='AI Article Generator',
    description='AI Article Generator Backend',
    version='0.1.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理"""
    return JSONResponse(
        status_code=200,
        content={
            "code": exc.error_code.code,
            "data": None,
            "message": exc.message
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.SYSTEM_ERROR,
            "data": None,
            "message": "系统异常"
        }
    )


app.include_router(user_router, prefix='/api')
