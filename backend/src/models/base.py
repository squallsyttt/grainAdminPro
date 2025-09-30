"""
SQLAlchemy Base 模型类
提供所有模型的基础字段和方法
"""
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TypeDecorator, CHAR

Base = declarative_base()


class UUID(TypeDecorator):
    """
    跨数据库兼容的 UUID 类型
    PostgreSQL: 使用原生 UUID 类型
    SQLite/其他: 使用 CHAR(32) 存储
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQL_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


class BaseModel(Base):
    """
    所有模型的基类
    包含通用字段：id, created_at, updated_at
    """

    __abstract__ = True

    id = Column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        comment="主键 UUID",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="创建时间",
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型转换为字典
        跳过以 _ 开头的私有属性和 SQLAlchemy 内部属性
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # 处理 UUID 类型
            if isinstance(value, uuid.UUID):
                value = str(value)
            # 处理 datetime 类型
            elif isinstance(value, datetime):
                value = value.isoformat()
            # 处理 Enum 类型
            elif hasattr(value, "value"):
                value = value.value
            result[column.name] = value
        return result

    def __repr__(self) -> str:
        """模型的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"