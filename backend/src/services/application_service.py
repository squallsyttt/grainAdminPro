"""
商家申请服务层
包含 CRUD 和业务逻辑（状态转换、验证）
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.enums import ApplicationStatus
from src.models.merchant_application import MerchantApplication
from src.models.qualification_file import QualificationFile
from src.models.enums import FileAuditStatus, QualificationFileType
from src.schemas.application import (
    CreateApplicationRequest,
    UpdateApplicationRequest,
)


class ApplicationService:
    """商家申请服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_application(
        self, data: CreateApplicationRequest
    ) -> MerchantApplication:
        """
        创建商家申请（草稿状态）

        Args:
            data: 创建申请请求数据

        Returns:
            MerchantApplication: 创建的申请对象
        """
        application = MerchantApplication(
            business_name=data.business_name,
            unified_social_credit=data.unified_social_credit,
            legal_person_name=data.legal_person_name,
            legal_person_id_number=data.legal_person_id_number,
            contact_name=data.contact_name,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            business_categories=data.business_categories,
            status=ApplicationStatus.DRAFT,
        )

        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)

        return application

    async def get_application(
        self,
        application_id: UUID,
        user_role: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> Optional[MerchantApplication]:
        """
        获取申请详情

        Args:
            application_id: 申请ID
            user_role: 用户角色（admin/merchant）
            user_id: 用户ID（用于权限验证）

        Returns:
            Optional[MerchantApplication]: 申请对象或None
        """
        query = (
            select(MerchantApplication)
            .where(MerchantApplication.id == application_id)
            .options(
                selectinload(MerchantApplication.audit_records),
                selectinload(MerchantApplication.qualification_files),
            )
        )

        result = await self.db.execute(query)
        application = result.scalar_one_or_none()

        # TODO: 实现权限验证（商家只能查询自己的申请）
        # if user_role == "merchant" and application.merchant_id != user_id:
        #     return None

        return application

    async def list_applications(
        self,
        filters: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[MerchantApplication], int]:
        """
        查询申请列表（支持分页和筛选）

        Args:
            filters: 筛选条件（status, business_name 等）
            page: 页码（从1开始）
            page_size: 每页数量（默认20，最大100）

        Returns:
            tuple: (申请列表, 总数)
        """
        # 限制分页大小
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size

        # 构建查询
        query = select(MerchantApplication)
        count_query = select(MerchantApplication.id)

        # 应用筛选条件
        if filters:
            conditions = []
            if "status" in filters:
                conditions.append(MerchantApplication.status == filters["status"])
            if "business_name" in filters:
                conditions.append(
                    MerchantApplication.business_name.ilike(f"%{filters['business_name']}%")
                )

            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))

        # 排序（最新提交的在前）
        query = query.order_by(
            MerchantApplication.submitted_at.desc().nulls_last(),
            MerchantApplication.created_at.desc(),
        )

        # 分页
        query = query.offset(offset).limit(page_size)

        # 执行查询
        result = await self.db.execute(query)
        applications = result.scalars().all()

        # 获取总数
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())

        return list(applications), total

    async def update_application(
        self,
        application_id: UUID,
        data: UpdateApplicationRequest,
    ) -> Optional[MerchantApplication]:
        """
        更新申请信息（仅允许 DRAFT 和 REQUIRE_SUPPLEMENT 状态修改）

        Args:
            application_id: 申请ID
            data: 更新数据

        Returns:
            Optional[MerchantApplication]: 更新后的申请对象或None
        """
        application = await self.get_application(application_id)
        if not application:
            return None

        # 验证状态（仅草稿和待补充状态可修改）
        if application.status not in [
            ApplicationStatus.DRAFT,
            ApplicationStatus.REQUIRE_SUPPLEMENT,
        ]:
            raise ValueError(
                f"申请状态为 {application.status.value}，不允许修改"
            )

        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)

        await self.db.commit()
        await self.db.refresh(application)

        return application

    async def submit_application(
        self, application_id: UUID
    ) -> MerchantApplication:
        """
        提交申请（从 DRAFT 或 REQUIRE_SUPPLEMENT 变更为 PENDING）

        Args:
            application_id: 申请ID

        Returns:
            MerchantApplication: 提交后的申请对象

        Raises:
            ValueError: 申请不存在、状态不允许提交或信息不完整
        """
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("申请不存在")

        # 验证状态
        if application.status not in [
            ApplicationStatus.DRAFT,
            ApplicationStatus.REQUIRE_SUPPLEMENT,
        ]:
            raise ValueError(
                f"申请状态为 {application.status.value}，不允许提交"
            )

        # 验证申请完整性
        if not self.validate_application_complete(application):
            raise ValueError("申请信息不完整，请检查必填字段和必需文件")

        # 更新状态
        application.status = ApplicationStatus.PENDING
        application.submitted_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(application)

        return application

    def validate_application_complete(
        self, application: MerchantApplication
    ) -> bool:
        """
        验证申请是否完整（所有必填字段和文件）

        Args:
            application: 申请对象

        Returns:
            bool: 是否完整
        """
        # 验证必填字段
        required_fields = [
            application.business_name,
            application.unified_social_credit,
            application.legal_person_name,
            application.legal_person_id_number,
            application.contact_name,
            application.contact_phone,
            application.contact_email,
            application.business_categories,
        ]

        if not all(required_fields):
            return False

        # 验证经营类目非空
        if not application.business_categories or len(application.business_categories) == 0:
            return False

        # 验证必需文件（营业执照、身份证正反面）
        required_file_types = [
            QualificationFileType.BUSINESS_LICENSE,
            QualificationFileType.ID_CARD_FRONT,
            QualificationFileType.ID_CARD_BACK,
        ]

        uploaded_file_types = [
            f.file_type for f in application.qualification_files
        ]

        for file_type in required_file_types:
            if file_type not in uploaded_file_types:
                return False

        return True

    async def delete_application(self, application_id: UUID) -> bool:
        """
        删除申请（仅允许删除草稿状态的申请）

        Args:
            application_id: 申请ID

        Returns:
            bool: 是否删除成功
        """
        application = await self.get_application(application_id)
        if not application:
            return False

        # 仅草稿状态可删除
        if application.status != ApplicationStatus.DRAFT:
            raise ValueError("仅草稿状态的申请可以删除")

        await self.db.delete(application)
        await self.db.commit()

        return True