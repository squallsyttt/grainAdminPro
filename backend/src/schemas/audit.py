"""
审核相关的 Pydantic schemas
用于API请求/响应的数据验证和序列化
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.models.enums import AuditAction, AuditResult


class CreateAuditRequest(BaseModel):
    """创建审核记录请求"""

    application_id: UUID = Field(..., description="申请ID")
    action: AuditAction = Field(..., description="审核动作")
    result: AuditResult = Field(..., description="审核结果")
    comment: Optional[str] = Field(None, description="审核意见")

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: Optional[str], info) -> Optional[str]:
        """验证审核意见：reject和request_supplement时必填"""
        if info.data.get("action") in [
            AuditAction.REJECT,
            AuditAction.REQUEST_SUPPLEMENT,
        ]:
            if not v or not v.strip():
                raise ValueError(f"审核动作为 {info.data.get('action').value} 时，审核意见必填")
        return v


class AuditResponse(BaseModel):
    """审核记录响应"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="审核记录ID")
    application_id: UUID = Field(..., description="申请ID")
    auditor_id: UUID = Field(..., description="审核员ID")
    auditor_name: str = Field(..., description="审核员姓名")
    action: AuditAction = Field(..., description="审核动作")
    result: AuditResult = Field(..., description="审核结果")
    comment: Optional[str] = Field(None, description="审核意见")
    created_at: datetime = Field(..., description="创建时间")


class AuditRecordSummary(BaseModel):
    """审核记录摘要（用于列表展示）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="审核记录ID")
    auditor_name: str = Field(..., description="审核员姓名")
    action: AuditAction = Field(..., description="审核动作")
    result: AuditResult = Field(..., description="审核结果")
    created_at: datetime = Field(..., description="创建时间")


class AuditHistoryResponse(BaseModel):
    """审核历史响应"""

    application_id: UUID = Field(..., description="申请ID")
    records: List[AuditResponse] = Field(..., description="审核记录列表")