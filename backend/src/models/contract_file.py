"""
合同档案模型
存储商家上传的线下签署合同照片
"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class ContractFile(BaseModel):
    """合同档案表"""

    __tablename__ = "contract_file"

    # 关联商家
    merchant_id = Column(
        String(20),
        ForeignKey("merchant_account.merchant_id", ondelete="CASCADE"),
        nullable=False,
        comment="关联商家账户 ID",
    )

    # 文件信息
    file_path = Column(
        String(500),
        nullable=False,
        comment="文件存储路径（相对路径或 S3 Key）",
    )

    file_size = Column(
        BigInteger, nullable=False, comment="文件大小（字节）"
    )

    file_type = Column(
        String(50),
        nullable=False,
        comment="文件类型（MIME type，如 image/jpeg）",
    )

    # 上传信息
    upload_by = Column(
        String(100), nullable=False, comment="上传人（商家用户名或平台管理员）"
    )

    uploaded_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, comment="上传时间"
    )

    # 关系
    merchant = relationship("MerchantAccount", back_populates="contract_files")

    # 约束和索引
    __table_args__ = (
        CheckConstraint(
            "file_size > 0 AND file_size <= 10485760",
            name="chk_contract_file_size",
        ),
        Index(
            "idx_contract_file_merchant_id",
            "merchant_id",
            "uploaded_at",
            postgresql_using="btree",
        ),
        Index("idx_contract_file_uploaded_at", "uploaded_at"),
    )

    def __repr__(self) -> str:
        return f"<ContractFile(id={self.id}, merchant_id={self.merchant_id}, file_path={self.file_path})>"

    def is_valid_type(self) -> bool:
        """验证文件类型是否允许"""
        allowed_types = {"image/jpeg", "image/png", "application/pdf"}
        return self.file_type in allowed_types