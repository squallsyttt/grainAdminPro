"""
商家账户模型
存储审核通过后自动创建的商家登录账户
"""
from typing import Dict, Any

from passlib.hash import bcrypt
from sqlalchemy import Column, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel
from src.models.enums import MerchantLevel, MerchantStatus


class MerchantAccount(BaseModel):
    """商家账户表"""

    __tablename__ = "merchant_account"

    # 商家编号（业务主键）
    merchant_id = Column(
        String(20),
        nullable=False,
        unique=True,
        comment="商家编号（如 M20250930001）",
    )

    # 登录凭证
    username = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="登录用户名（默认使用联系人电话或邮箱）",
    )

    password_hash = Column(
        String(255), nullable=False, comment="密码哈希（使用 bcrypt）"
    )

    # 商家等级和状态
    level = Column(
        Enum(MerchantLevel),
        nullable=False,
        default=MerchantLevel.NORMAL,
        comment="商家等级",
    )

    status = Column(
        Enum(MerchantStatus),
        nullable=False,
        default=MerchantStatus.ACTIVE,
        comment="账户状态",
    )

    # 关联的入驻申请
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchant_application.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        comment="关联的入驻申请 ID（一个申请对应一个账户）",
    )

    # 关系
    application = relationship("MerchantApplication", backref="account")

    contract_files = relationship(
        "ContractFile",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )

    qualification_files = relationship(
        "QualificationFile",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )

    # 索引
    __table_args__ = (
        Index("idx_merchant_account_merchant_id", "merchant_id", unique=True),
        Index("idx_merchant_account_username", "username", unique=True),
        Index("idx_merchant_account_level_status", "level", "status"),
        Index("idx_merchant_account_application_id", "application_id"),
    )

    def __repr__(self) -> str:
        return f"<MerchantAccount(id={self.id}, merchant_id={self.merchant_id}, username={self.username})>"

    def set_password(self, plain_password: str) -> None:
        """设置密码（自动哈希）"""
        self.password_hash = bcrypt.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        """验证密码"""
        return bcrypt.verify(plain_password, self.password_hash)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含密码哈希）"""
        result = super().to_dict()
        result.pop("password_hash", None)
        return result

    def is_active(self) -> bool:
        """判断账户是否激活"""
        return self.status == MerchantStatus.ACTIVE