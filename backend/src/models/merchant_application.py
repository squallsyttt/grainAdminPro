"""
商家申请模型
存储商家入驻申请的核心信息
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Enum, Index, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.models.base import BaseModel
from src.models.enums import ApplicationStatus


class MerchantApplication(BaseModel):
    """商家入驻申请表"""

    __tablename__ = "merchant_application"

    # 企业基本信息
    business_name = Column(
        String(200), nullable=False, comment="企业名称"
    )

    unified_social_credit = Column(
        String(18),
        nullable=False,
        unique=True,
        comment="统一社会信用代码（营业执照号）",
    )

    # 法人信息
    legal_person_name = Column(
        String(100), nullable=False, comment="法人姓名"
    )

    legal_person_id_number = Column(
        String(18),
        nullable=False,
        comment="法人身份证号（敏感信息，暂用明文，后续加密）",
    )

    # 联系方式
    contact_name = Column(String(100), nullable=False, comment="联系人姓名")

    contact_phone = Column(
        String(20),
        nullable=False,
        comment="联系电话（敏感信息，暂用明文，后续加密）",
    )

    contact_email = Column(String(255), nullable=False, comment="联系邮箱")

    # 经营信息
    business_categories = Column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        comment='经营类目（JSON 数组，如 ["食品", "服装"]）',
    )

    # 申请状态
    status = Column(
        Enum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.DRAFT,
        comment="申请状态",
    )

    submitted_at = Column(
        DateTime, nullable=True, comment="提交时间（从草稿状态提交时记录）"
    )

    # 关系
    audit_records = relationship(
        "AuditRecord",
        back_populates="application",
        cascade="all, delete-orphan",
    )

    qualification_files = relationship(
        "QualificationFile",
        back_populates="application",
        cascade="all, delete-orphan",
    )

    # 索引
    __table_args__ = (
        Index("idx_merchant_application_status", "status", "created_at"),
        Index(
            "idx_merchant_application_submitted_at",
            "submitted_at",
            postgresql_using="btree",
        ),
        Index(
            "idx_merchant_application_credit_code", "unified_social_credit"
        ),
        # 全文搜索索引（暂时简化，后续可启用 pg_trgm）
        Index("idx_merchant_application_business_name", "business_name"),
    )

    def __repr__(self) -> str:
        return f"<MerchantApplication(id={self.id}, business_name={self.business_name}, status={self.status.value})>"

    def submit(self) -> None:
        """提交申请（从草稿状态变更为待审核）"""
        if self.status == ApplicationStatus.DRAFT:
            self.status = ApplicationStatus.PENDING
            self.submitted_at = datetime.utcnow()

    def is_editable(self) -> bool:
        """判断申请是否可编辑"""
        return self.status in [
            ApplicationStatus.DRAFT,
            ApplicationStatus.REQUIRE_SUPPLEMENT,
        ]