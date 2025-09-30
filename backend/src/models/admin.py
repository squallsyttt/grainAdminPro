"""
管理员用户模型
存储后台管理员账户信息
"""
from typing import Any, Dict

from sqlalchemy import Boolean, Column, Index, String

from src.models.base import BaseModel


class AdminUser(BaseModel):
    """管理员用户表"""

    __tablename__ = "admin_user"

    # 用户名（登录凭证）
    username = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="登录用户名",
    )

    # 密码哈希
    password_hash = Column(
        String(255),
        nullable=False,
        comment="密码哈希（使用 bcrypt）",
    )

    # 姓名
    name = Column(
        String(100),
        nullable=False,
        comment="管理员姓名",
    )

    # 邮箱
    email = Column(
        String(255),
        nullable=True,
        unique=True,
        comment="邮箱（可选，用于登录和通知）",
    )

    # 账户状态
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="账户是否激活",
    )

    # 索引
    __table_args__ = (
        Index("idx_admin_user_username", "username", unique=True),
        Index("idx_admin_user_email", "email", unique=True),
        Index("idx_admin_user_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<AdminUser(id={self.id}, username={self.username}, name={self.name})>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含密码哈希）"""
        result = super().to_dict()
        result.pop("password_hash", None)
        return result
