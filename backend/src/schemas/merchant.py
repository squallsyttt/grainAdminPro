"""
商家账户相关的 Pydantic schemas
用于API请求/响应的数据验证和序列化
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.models.enums import MerchantLevel, MerchantStatus


class MerchantResponse(BaseModel):
    """商家账户响应（不包含敏感信息）"""

    model_config = ConfigDict(from_attributes=True)

    merchant_id: str = Field(..., description="商家编号", examples=["M20250930001"])
    username: str = Field(..., description="登录用户名")
    level: MerchantLevel = Field(..., description="商家等级")
    status: MerchantStatus = Field(..., description="账户状态")
    application_id: UUID = Field(..., description="关联的入驻申请ID")
    created_at: datetime = Field(..., description="创建时间")


class UpdateMerchantRequest(BaseModel):
    """更新商家信息请求（仅允许更新联系方式）"""

    contact_phone: Optional[str] = Field(
        None, pattern=r"^1[3-9]\d{9}$", description="联系电话"
    )
    contact_email: Optional[EmailStr] = Field(None, description="联系邮箱")