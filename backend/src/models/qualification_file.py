"""
资质文件模型
存储商家申请时上传的资质证件(营业执照、身份证等)
"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel
from src.models.enums import FileAuditStatus, QualificationFileType


class QualificationFile(BaseModel):
    """资质文件表"""

    __tablename__ = "qualification_file"

    # 关联申请和商家
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchant_application.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联商家申请 ID",
    )

    merchant_id = Column(
        String(20),
        ForeignKey("merchant_account.merchant_id", ondelete="SET NULL"),
        nullable=True,
        comment="关联商家账户 ID（审核通过后关联）",
    )

    # 文件信息
    file_type = Column(
        Enum(QualificationFileType),
        nullable=False,
        comment="文件类型",
    )

    file_path = Column(
        String(500), nullable=False, comment="文件存储路径"
    )

    file_size = Column(
        BigInteger, nullable=False, comment="文件大小（字节）"
    )

    # 审核状态
    audit_status = Column(
        Enum(FileAuditStatus),
        nullable=False,
        default=FileAuditStatus.PENDING,
        comment="审核状态",
    )

    # 上传时间
    uploaded_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, comment="上传时间"
    )

    # 关系
    application = relationship(
        "MerchantApplication", back_populates="qualification_files"
    )

    merchant = relationship(
        "MerchantAccount", back_populates="qualification_files"
    )

    # 约束和索引
    __table_args__ = (
        CheckConstraint(
            "file_size > 0 AND file_size <= 10485760",
            name="chk_qualification_file_size",
        ),
        Index(
            "idx_qualification_file_application_id",
            "application_id",
            "file_type",
        ),
        Index("idx_qualification_file_merchant_id", "merchant_id"),
        Index("idx_qualification_file_audit_status", "audit_status"),
    )

    def __repr__(self) -> str:
        return f"<QualificationFile(id={self.id}, application_id={self.application_id}, file_type={self.file_type.value})>"

    def is_required_type(self) -> bool:
        """判断是否为必须上传的文件类型"""
        required_types = {
            QualificationFileType.BUSINESS_LICENSE,
            QualificationFileType.ID_CARD_FRONT,
            QualificationFileType.ID_CARD_BACK,
        }
        return self.file_type in required_types

    def is_valid_mime_type(self) -> bool:
        """验证文件 MIME 类型是否允许"""
        # 这里需要检查实际文件的 MIME type
        # 简化实现,后续在服务层验证
        return True