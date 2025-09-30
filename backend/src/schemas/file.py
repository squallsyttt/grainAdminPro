"""
文件上传相关的 Pydantic schemas
用于API请求/响应的数据验证和序列化
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.models.enums import FileAuditStatus, QualificationFileType


class FileUploadResponse(BaseModel):
    """文件上传响应"""

    model_config = ConfigDict(from_attributes=True)

    file_id: UUID = Field(..., description="文件ID")
    file_path: str = Field(..., description="文件存储路径")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: str = Field(..., description="文件类型")
    uploaded_at: datetime = Field(..., description="上传时间")


class FileInfo(BaseModel):
    """文件信息（用于列表展示）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="文件ID")
    file_type: QualificationFileType = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小（字节）")
    audit_status: FileAuditStatus = Field(..., description="审核状态")
    uploaded_at: datetime = Field(..., description="上传时间")