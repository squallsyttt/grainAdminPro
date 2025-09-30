"""
商家申请相关的 Pydantic schemas
用于API请求/响应的数据验证和序列化
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from src.models.enums import ApplicationStatus


class CreateApplicationRequest(BaseModel):
    """创建商家申请请求"""

    business_name: str = Field(
        ..., max_length=200, description="企业名称", examples=["测试科技有限公司"]
    )
    unified_social_credit: str = Field(
        ...,
        pattern=r"^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$",
        description="统一社会信用代码（营业执照号）",
        examples=["91110108MA01234567"],
    )
    legal_person_name: str = Field(
        ..., max_length=100, description="法人姓名", examples=["张三"]
    )
    legal_person_id_number: str = Field(
        ...,
        pattern=r"^\d{17}[\dXx]$",
        description="法人身份证号",
        examples=["110101199001011234"],
    )
    contact_name: str = Field(..., max_length=100, description="联系人姓名", examples=["李四"])
    contact_phone: str = Field(
        ...,
        pattern=r"^1[3-9]\d{9}$",
        description="联系电话",
        examples=["13800138000"],
    )
    contact_email: EmailStr = Field(
        ..., description="联系邮箱", examples=["contact@example.com"]
    )
    business_categories: List[str] = Field(
        ...,
        min_length=1,
        description='经营类目（数组，如 ["食品", "日用品"]）',
        examples=[["食品", "日用品"]],
    )

    @field_validator("unified_social_credit")
    @classmethod
    def validate_unified_social_credit(cls, v: str) -> str:
        """验证统一社会信用代码格式"""
        if not v or len(v) != 18:
            raise ValueError("统一社会信用代码必须为18位")
        return v.upper()

    @field_validator("legal_person_id_number")
    @classmethod
    def validate_id_number(cls, v: str) -> str:
        """验证身份证号格式"""
        if not v or len(v) != 18:
            raise ValueError("身份证号必须为18位")
        return v.upper()

    @field_validator("business_categories")
    @classmethod
    def validate_business_categories(cls, v: List[str]) -> List[str]:
        """验证经营类目非空"""
        if not v:
            raise ValueError("经营类目不能为空")
        return v


class UpdateApplicationRequest(BaseModel):
    """更新商家申请请求（可选字段）"""

    contact_name: Optional[str] = Field(None, max_length=100, description="联系人姓名")
    contact_phone: Optional[str] = Field(
        None, pattern=r"^1[3-9]\d{9}$", description="联系电话"
    )
    contact_email: Optional[EmailStr] = Field(None, description="联系邮箱")
    business_categories: Optional[List[str]] = Field(None, description="经营类目")


class ApplicationResponse(BaseModel):
    """商家申请响应（基础信息）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="申请ID")
    business_name: str = Field(..., description="企业名称")
    unified_social_credit: str = Field(..., description="统一社会信用代码")
    legal_person_name: str = Field(..., description="法人姓名")
    contact_name: str = Field(..., description="联系人姓名")
    contact_phone: str = Field(..., description="联系电话")
    contact_email: str = Field(..., description="联系邮箱")
    business_categories: List[str] = Field(..., description="经营类目")
    status: ApplicationStatus = Field(..., description="申请状态")
    submitted_at: Optional[datetime] = Field(None, description="提交时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ApplicationDetailResponse(ApplicationResponse):
    """商家申请详情响应（包含关联数据）"""

    qualification_files: List["FileInfo"] = Field(default_factory=list, description="资质文件列表")
    audit_records: List["AuditRecordSummary"] = Field(
        default_factory=list, description="审核记录列表"
    )


class ApplicationListResponse(BaseModel):
    """商家申请列表响应（带分页）"""

    items: List[ApplicationResponse] = Field(..., description="申请列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


# Forward references for circular imports
from src.schemas.audit import AuditRecordSummary  # noqa: E402
from src.schemas.file import FileInfo  # noqa: E402

ApplicationDetailResponse.model_rebuild()