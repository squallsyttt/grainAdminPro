"""
文件服务层
包含文件上传、下载、验证、权限控制
"""
import hashlib
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.file_storage import file_storage
from src.models.contract_file import ContractFile
from src.models.qualification_file import QualificationFile
from src.models.enums import QualificationFileType, FileAuditStatus


class FileService:
    """文件服务"""

    # 允许的文件类型
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "application/pdf",
    }

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

    # 最大文件大小（10MB）
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_qualification_file(
        self,
        file: UploadFile,
        application_id: UUID,
        file_type: QualificationFileType,
    ) -> QualificationFile:
        """
        上传资质文件（营业执照、身份证等）

        Args:
            file: 上传的文件对象
            application_id: 关联的申请ID
            file_type: 文件类型

        Returns:
            QualificationFile: 创建的资质文件记录

        Raises:
            ValueError: 文件验证失败
        """
        # 验证文件
        await self.validate_file(file)

        # 生成文件路径
        file_extension = Path(file.filename).suffix
        file_name = f"{file_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
        file_path = file_storage.generate_file_path(
            "applications", str(application_id), file_name
        )

        # 保存文件
        file_storage.save_file(file.file, file_path)

        # 创建数据库记录
        qualification_file = QualificationFile(
            application_id=application_id,
            file_type=file_type,
            file_path=file_path,
            file_size=file.size,
            audit_status=FileAuditStatus.PENDING,
            uploaded_at=datetime.utcnow(),
        )

        self.db.add(qualification_file)
        await self.db.commit()
        await self.db.refresh(qualification_file)

        return qualification_file

    async def upload_contract_file(
        self, file: UploadFile, merchant_id: str, upload_by: str
    ) -> ContractFile:
        """
        上传合同文件（商家上传线下签署的合同照片）

        Args:
            file: 上传的文件对象
            merchant_id: 商家编号
            upload_by: 上传人

        Returns:
            ContractFile: 创建的合同文件记录

        Raises:
            ValueError: 文件验证失败
        """
        # 验证文件
        await self.validate_file(file)

        # 生成文件路径
        file_extension = Path(file.filename).suffix
        file_name = f"contract_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
        file_path = file_storage.generate_file_path(
            "contracts", merchant_id, file_name
        )

        # 保存文件
        file_storage.save_file(file.file, file_path)

        # 获取文件MIME类型
        mime_type, _ = mimetypes.guess_type(file.filename)

        # 创建数据库记录
        contract_file = ContractFile(
            merchant_id=merchant_id,
            file_path=file_path,
            file_size=file.size,
            file_type=mime_type or "application/octet-stream",
            upload_by=upload_by,
            uploaded_at=datetime.utcnow(),
        )

        self.db.add(contract_file)
        await self.db.commit()
        await self.db.refresh(contract_file)

        return contract_file

    async def validate_file(self, file: UploadFile) -> bool:
        """
        验证文件（类型、大小、Magic Bytes）

        Args:
            file: 上传的文件对象

        Returns:
            bool: 是否验证通过

        Raises:
            ValueError: 验证失败的具体原因
        """
        # 验证文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"不允许的文件类型: {file_extension}。允许的类型: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # 验证文件大小
        if file.size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"文件大小超过限制: {file.size} bytes。最大允许: {self.MAX_FILE_SIZE} bytes"
            )

        # 验证 MIME 类型
        mime_type = file.content_type
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(
                f"不允许的文件 MIME 类型: {mime_type}。允许的类型: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )

        # 验证 Magic Bytes（文件头）
        file.file.seek(0)
        file_header = file.file.read(20)
        file.file.seek(0)

        if not self._verify_magic_bytes(file_header, mime_type):
            raise ValueError("文件内容与文件类型不匹配（可能是伪造的文件类型）")

        return True

    def _verify_magic_bytes(self, file_header: bytes, mime_type: str) -> bool:
        """
        验证文件 Magic Bytes（文件头）

        Args:
            file_header: 文件头字节
            mime_type: MIME 类型

        Returns:
            bool: 是否匹配
        """
        # 常见文件的 Magic Bytes
        magic_bytes = {
            "image/jpeg": [b"\xFF\xD8\xFF"],
            "image/png": [b"\x89\x50\x4E\x47"],
            "application/pdf": [b"%PDF-"],
        }

        if mime_type not in magic_bytes:
            # 未知类型,默认通过
            return True

        # 检查文件头是否匹配
        for magic in magic_bytes[mime_type]:
            if file_header.startswith(magic):
                return True

        return False

    async def generate_signed_url(
        self,
        file_id: UUID,
        user_id: Optional[UUID] = None,
        expiration_hours: int = 1,
    ) -> str:
        """
        生成文件的签名URL（用于安全下载）

        Args:
            file_id: 文件ID
            user_id: 用户ID（用于权限验证）
            expiration_hours: 有效期（小时）

        Returns:
            str: 签名URL

        Note:
            简化实现,返回文件路径
            生产环境应实现真正的签名URL（如使用JWT Token）
        """
        # TODO: 实现真正的签名URL
        # 1. 验证用户权限（用户只能访问自己的文件）
        # 2. 生成带过期时间的签名Token
        # 3. 返回包含Token的URL

        # 简化实现：直接返回文件相对路径
        qualification_file = await self.get_qualification_file(file_id)
        if qualification_file:
            return qualification_file.file_path

        contract_file = await self.get_contract_file(file_id)
        if contract_file:
            return contract_file.file_path

        raise ValueError("文件不存在")

    async def delete_file(self, file_id: UUID) -> bool:
        """
        删除文件（仅标记删除,不实际删除物理文件）

        Args:
            file_id: 文件ID

        Returns:
            bool: 是否删除成功

        Note:
            实际生产环境建议使用软删除（添加 deleted_at 字段）
            物理文件通过定时任务清理
        """
        # TODO: 实现软删除机制
        # 1. 添加 deleted_at 字段到文件模型
        # 2. 标记文件为已删除
        # 3. 定时任务清理过期的已删除文件

        qualification_file = await self.get_qualification_file(file_id)
        if qualification_file:
            await self.db.delete(qualification_file)
            await self.db.commit()
            # 删除物理文件
            file_storage.delete_file(qualification_file.file_path)
            return True

        contract_file = await self.get_contract_file(file_id)
        if contract_file:
            await self.db.delete(contract_file)
            await self.db.commit()
            # 删除物理文件
            file_storage.delete_file(contract_file.file_path)
            return True

        return False

    async def get_qualification_file(
        self, file_id: UUID
    ) -> Optional[QualificationFile]:
        """
        根据ID获取资质文件

        Args:
            file_id: 文件ID

        Returns:
            Optional[QualificationFile]: 资质文件或None
        """
        query = select(QualificationFile).where(
            QualificationFile.id == file_id
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_contract_file(
        self, file_id: UUID
    ) -> Optional[ContractFile]:
        """
        根据ID获取合同文件

        Args:
            file_id: 文件ID

        Returns:
            Optional[ContractFile]: 合同文件或None
        """
        query = select(ContractFile).where(ContractFile.id == file_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_application_files(
        self, application_id: UUID
    ) -> list[QualificationFile]:
        """
        获取申请的所有资质文件

        Args:
            application_id: 申请ID

        Returns:
            list[QualificationFile]: 资质文件列表
        """
        query = (
            select(QualificationFile)
            .where(QualificationFile.application_id == application_id)
            .order_by(QualificationFile.uploaded_at.desc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_merchant_contracts(
        self, merchant_id: str
    ) -> list[ContractFile]:
        """
        获取商家的所有合同文件

        Args:
            merchant_id: 商家编号

        Returns:
            list[ContractFile]: 合同文件列表
        """
        query = (
            select(ContractFile)
            .where(ContractFile.merchant_id == merchant_id)
            .order_by(ContractFile.uploaded_at.desc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())