"""
结构化日志模块
提供 JSON 格式日志和 Correlation ID 追踪功能
"""
import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

from src.core.config import settings

# Correlation ID 上下文变量（用于在同一请求中共享）
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str:
    """
    获取当前请求的 Correlation ID

    Returns:
        str: Correlation ID（如果不存在则生成新的）
    """
    cid = correlation_id_var.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id_var.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """
    设置当前请求的 Correlation ID

    Args:
        cid: Correlation ID
    """
    correlation_id_var.set(cid)


def clear_correlation_id() -> None:
    """清除当前请求的 Correlation ID"""
    correlation_id_var.set(None)


class JSONFormatter(logging.Formatter):
    """
    JSON 格式的日志格式化器

    输出结构化的 JSON 日志，方便日志收集和分析
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        将日志记录格式化为 JSON 字符串

        Args:
            record: 日志记录对象

        Returns:
            str: JSON 格式的日志字符串
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        # 添加额外的上下文信息
        if hasattr(record, "extra_fields") and record.extra_fields:
            log_data.update(record.extra_fields)

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # 添加文件位置信息（仅在调试模式）
        if settings.DEBUG:
            log_data["location"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """
    结构化日志记录器

    提供带上下文信息的结构化日志记录功能
    """

    def __init__(self, name: str):
        """
        初始化日志记录器

        Args:
            name: 日志记录器名称
        """
        self.logger = logging.getLogger(name)

    def _log(
        self,
        level: int,
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """
        记录日志的内部方法

        Args:
            level: 日志级别
            message: 日志消息
            extra_fields: 额外的字段（会被添加到 JSON 日志中）
            exc_info: 是否包含异常信息
        """
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            None if not exc_info else sys.exc_info(),
        )

        # 添加额外字段
        if extra_fields:
            record.extra_fields = extra_fields  # type: ignore

        self.logger.handle(record)

    def debug(self, message: str, **extra_fields: Any) -> None:
        """记录 DEBUG 级别日志"""
        self._log(logging.DEBUG, message, extra_fields)

    def info(self, message: str, **extra_fields: Any) -> None:
        """记录 INFO 级别日志"""
        self._log(logging.INFO, message, extra_fields)

    def warning(self, message: str, **extra_fields: Any) -> None:
        """记录 WARNING 级别日志"""
        self._log(logging.WARNING, message, extra_fields)

    def error(self, message: str, **extra_fields: Any) -> None:
        """记录 ERROR 级别日志"""
        self._log(logging.ERROR, message, extra_fields, exc_info=True)

    def critical(self, message: str, **extra_fields: Any) -> None:
        """记录 CRITICAL 级别日志"""
        self._log(logging.CRITICAL, message, extra_fields, exc_info=True)


def setup_logging() -> None:
    """
    配置应用程序日志系统

    在应用启动时调用，配置日志格式、级别和输出目标
    """
    # 设置根日志级别
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # 清除现有的处理器
    root_logger.handlers.clear()

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # 使用 JSON 格式化器
    json_formatter = JSONFormatter()
    console_handler.setFormatter(json_formatter)

    # 添加处理器
    root_logger.addHandler(console_handler)

    # 设置第三方库的日志级别（减少噪音）
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> StructuredLogger:
    """
    获取结构化日志记录器

    Args:
        name: 日志记录器名称（通常使用 __name__）

    Returns:
        StructuredLogger: 结构化日志记录器实例

    Usage:
        >>> logger = get_logger(__name__)
        >>> logger.info("用户登录", user_id="123", ip="192.168.1.1")
    """
    return StructuredLogger(name)