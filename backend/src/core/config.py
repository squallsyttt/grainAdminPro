"""
配置管理模块
从环境变量加载应用配置
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 应用配置
    APP_NAME: str = "grainAdminPro"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # Celery 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # JWT 配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,application/pdf"

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:8001,http://localhost:8002"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    CORS_ALLOW_HEADERS: str = "*"

    # 日志配置
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"

    # 安全配置
    BCRYPT_ROUNDS: int = 12

    # 缓存配置
    CACHE_DEFAULT_TTL: int = 3600
    CACHE_MERCHANT_INFO_TTL: int = 3600
    CACHE_AUDITOR_PERMISSIONS_TTL: int = 900

    # 前端 URL 配置
    ADMIN_FRONTEND_URL: str = "http://localhost:8001"
    MERCHANT_FRONTEND_URL: str = "http://localhost:8002"

    # 性能监控配置
    SLOW_QUERY_THRESHOLD_MS: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量


# 全局配置实例
settings = Settings()