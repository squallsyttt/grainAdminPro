"""
FastAPI 主应用入口
grainAdminPro - 商家入驻管理系统 Backend API
"""
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.redis import redis_manager
from src.core.logging import (
    setup_logging,
    get_logger,
    set_correlation_id,
    clear_correlation_id,
    get_correlation_id,
)

# 初始化日志系统
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理"""
    # 启动时执行
    logger.info("启动 API 服务", app_name=settings.APP_NAME, env=settings.APP_ENV, debug=settings.DEBUG)

    # 初始化 Redis 连接
    await redis_manager.connect()
    logger.info("Redis 连接成功")

    yield  # 应用运行中

    # 关闭时执行
    logger.info("正在关闭服务")
    await redis_manager.disconnect()
    logger.info("Redis 连接已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="商家入驻管理系统 - Backend API",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# 配置 CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(","),
    allow_headers=settings.CORS_ALLOW_HEADERS.split(",")
    if settings.CORS_ALLOW_HEADERS != "*"
    else ["*"],
)


# ========================================
# 中间件: Correlation ID + 请求/响应日志
# ========================================

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """
    Correlation ID 中间件

    为每个请求生成或提取 Correlation ID，并添加到响应头中
    """
    # 1. 获取或生成 Correlation ID
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        import uuid
        correlation_id = str(uuid.uuid4())

    # 2. 设置到上下文变量中
    set_correlation_id(correlation_id)

    # 3. 处理请求
    response = await call_next(request)

    # 4. 添加到响应头
    response.headers["X-Correlation-ID"] = correlation_id

    # 5. 清除上下文
    clear_correlation_id()

    return response


@app.middleware("http")
async def request_response_logging_middleware(request: Request, call_next):
    """
    请求/响应日志中间件

    记录所有 HTTP 请求和响应的详细信息
    """
    # 记录请求开始时间
    start_time = time.time()

    # 提取请求信息
    request_info = {
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }

    # 记录请求日志
    logger.info(
        "收到 HTTP 请求",
        **request_info
    )

    try:
        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        duration_ms = (time.time() - start_time) * 1000

        # 记录响应日志
        logger.info(
            "HTTP 响应",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            **request_info
        )

        return response

    except Exception as e:
        # 计算处理时间
        duration_ms = (time.time() - start_time) * 1000

        # 记录错误日志
        logger.error(
            "HTTP 请求处理失败",
            error=str(e),
            duration_ms=round(duration_ms, 2),
            **request_info
        )

        # 返回 500 错误
        return JSONResponse(
            status_code=500,
            content={
                "detail": "服务器内部错误",
                "correlation_id": get_correlation_id()
            }
        )


@app.get("/health")
async def health_check() -> dict:
    """健康检查端点"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "version": "0.1.0",
    }


@app.get("/")
async def root() -> dict:
    """根路径"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# 注册路由
from src.api.v1 import applications, audits, auth, files, merchants

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

app.include_router(
    applications.router,
    prefix="/api/v1/applications",
    tags=["applications"]
)

app.include_router(
    audits.router,
    prefix="/api/v1/audits",
    tags=["audits"]
)

app.include_router(
    merchants.router,
    prefix="/api/v1/merchants",
    tags=["merchants"]
)

app.include_router(
    files.router,
    prefix="/api/v1/files",
    tags=["files"]
)