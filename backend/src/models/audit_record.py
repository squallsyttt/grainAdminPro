"""
审核记录模型
记录商家申请的每一次审核操作,确保审核过程可追溯
"""
from sqlalchemy import Column, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel
from src.models.enums import AuditAction, AuditResult


class AuditRecord(BaseModel):
    """审核记录表"""

    __tablename__ = "audit_record"

    # 关联申请
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchant_application.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联商家申请 ID",
    )

    # 审核员信息
    auditor_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        comment="审核员用户 ID（关联用户表，本 feature 未实现）",
    )

    auditor_name = Column(
        String(100),
        nullable=False,
        comment="审核员姓名（冗余存储，便于历史查询）",
    )

    # 审核操作
    action = Column(
        Enum(AuditAction), nullable=False, comment="审核动作"
    )

    result = Column(Enum(AuditResult), nullable=False, comment="审核结果")

    comment = Column(Text, nullable=True, comment="审核意见/备注")

    # 关系
    application = relationship(
        "MerchantApplication", back_populates="audit_records"
    )

    # 索引
    __table_args__ = (
        Index(
            "idx_audit_record_application_id",
            "application_id",
            "created_at",
            postgresql_using="btree",
        ),
        Index("idx_audit_record_auditor_id", "auditor_id"),
        Index("idx_audit_record_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditRecord(id={self.id}, application_id={self.application_id}, action={self.action.value}, result={self.result.value})>"

    def requires_comment(self) -> bool:
        """判断当前审核动作是否必须填写审核意见"""
        return self.action in [
            AuditAction.REJECT,
            AuditAction.REQUEST_SUPPLEMENT,
        ]