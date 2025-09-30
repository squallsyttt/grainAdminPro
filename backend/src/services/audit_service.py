"""
审核服务层
包含审核工作流和商家账户自动创建
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.enums import (
    ApplicationStatus,
    AuditAction,
    AuditResult,
)
from src.models.merchant_application import MerchantApplication
from src.models.audit_record import AuditRecord
from src.schemas.audit import CreateAuditRequest


class AuditService:
    """审核服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_review(
        self, application_id: UUID, auditor_id: UUID, auditor_name: str
    ) -> AuditRecord:
        """
        开始审核（状态从 PENDING 变更为 UNDER_REVIEW）

        Args:
            application_id: 申请ID
            auditor_id: 审核员ID
            auditor_name: 审核员姓名

        Returns:
            AuditRecord: 审核记录

        Raises:
            ValueError: 申请不存在或状态不允许审核
        """
        # 获取申请
        application = await self._get_application(application_id)
        if not application:
            raise ValueError("申请不存在")

        # 验证状态
        if application.status != ApplicationStatus.PENDING:
            raise ValueError(
                f"申请状态为 {application.status.value}，不允许开始审核"
            )

        # 创建审核记录
        audit_record = AuditRecord(
            application_id=application_id,
            auditor_id=auditor_id,
            auditor_name=auditor_name,
            action=AuditAction.START_REVIEW,
            result=AuditResult.IN_PROGRESS,
            comment="开始审核",
        )

        # 更新申请状态
        application.status = ApplicationStatus.UNDER_REVIEW

        self.db.add(audit_record)
        await self.db.commit()
        await self.db.refresh(audit_record)

        return audit_record

    async def approve_application(
        self,
        application_id: UUID,
        auditor_id: UUID,
        auditor_name: str,
        comment: str,
    ) -> AuditRecord:
        """
        审核通过（状态变更为 APPROVED，自动创建商家账户）

        Args:
            application_id: 申请ID
            auditor_id: 审核员ID
            auditor_name: 审核员姓名
            comment: 审核意见

        Returns:
            AuditRecord: 审核记录

        Raises:
            ValueError: 申请不存在或状态不允许审核
        """
        # 获取申请
        application = await self._get_application(application_id)
        if not application:
            raise ValueError("申请不存在")

        # 验证状态
        if application.status != ApplicationStatus.UNDER_REVIEW:
            raise ValueError(
                f"申请状态为 {application.status.value}，不允许审核通过"
            )

        # 创建审核记录
        audit_record = AuditRecord(
            application_id=application_id,
            auditor_id=auditor_id,
            auditor_name=auditor_name,
            action=AuditAction.APPROVE,
            result=AuditResult.APPROVED,
            comment=comment or "审核通过",
        )

        # 更新申请状态
        application.status = ApplicationStatus.APPROVED

        self.db.add(audit_record)
        await self.db.commit()
        await self.db.refresh(audit_record)

        # 自动创建商家账户
        await self._create_merchant_account(application)

        return audit_record

    async def reject_application(
        self,
        application_id: UUID,
        auditor_id: UUID,
        auditor_name: str,
        comment: str,
    ) -> AuditRecord:
        """
        审核拒绝（状态变更为 REJECTED）

        Args:
            application_id: 申请ID
            auditor_id: 审核员ID
            auditor_name: 审核员姓名
            comment: 拒绝原因（必填）

        Returns:
            AuditRecord: 审核记录

        Raises:
            ValueError: 申请不存在、状态不允许或缺少拒绝原因
        """
        # 验证拒绝原因
        if not comment or not comment.strip():
            raise ValueError("拒绝申请时必须填写拒绝原因")

        # 获取申请
        application = await self._get_application(application_id)
        if not application:
            raise ValueError("申请不存在")

        # 验证状态
        if application.status != ApplicationStatus.UNDER_REVIEW:
            raise ValueError(
                f"申请状态为 {application.status.value}，不允许审核拒绝"
            )

        # 创建审核记录
        audit_record = AuditRecord(
            application_id=application_id,
            auditor_id=auditor_id,
            auditor_name=auditor_name,
            action=AuditAction.REJECT,
            result=AuditResult.REJECTED,
            comment=comment,
        )

        # 更新申请状态
        application.status = ApplicationStatus.REJECTED

        self.db.add(audit_record)
        await self.db.commit()
        await self.db.refresh(audit_record)

        return audit_record

    async def request_supplement(
        self,
        application_id: UUID,
        auditor_id: UUID,
        auditor_name: str,
        comment: str,
    ) -> AuditRecord:
        """
        要求补充材料（状态变更为 REQUIRE_SUPPLEMENT）

        Args:
            application_id: 申请ID
            auditor_id: 审核员ID
            auditor_name: 审核员姓名
            comment: 需要补充的材料说明（必填）

        Returns:
            AuditRecord: 审核记录

        Raises:
            ValueError: 申请不存在、状态不允许或缺少补充说明
        """
        # 验证补充说明
        if not comment or not comment.strip():
            raise ValueError("要求补充材料时必须说明需要补充的内容")

        # 获取申请
        application = await self._get_application(application_id)
        if not application:
            raise ValueError("申请不存在")

        # 验证状态
        if application.status != ApplicationStatus.UNDER_REVIEW:
            raise ValueError(
                f"申请状态为 {application.status.value}，不允许要求补充材料"
            )

        # 创建审核记录
        audit_record = AuditRecord(
            application_id=application_id,
            auditor_id=auditor_id,
            auditor_name=auditor_name,
            action=AuditAction.REQUEST_SUPPLEMENT,
            result=AuditResult.PENDING_SUPPLEMENT,
            comment=comment,
        )

        # 更新申请状态
        application.status = ApplicationStatus.REQUIRE_SUPPLEMENT

        self.db.add(audit_record)
        await self.db.commit()
        await self.db.refresh(audit_record)

        return audit_record

    async def get_audit_history(
        self, application_id: UUID
    ) -> List[AuditRecord]:
        """
        获取申请的审核历史（按时间倒序）

        Args:
            application_id: 申请ID

        Returns:
            List[AuditRecord]: 审核记录列表
        """
        query = (
            select(AuditRecord)
            .where(AuditRecord.application_id == application_id)
            .order_by(AuditRecord.created_at.desc())
        )

        result = await self.db.execute(query)
        records = result.scalars().all()

        return list(records)

    async def _get_application(
        self, application_id: UUID
    ) -> Optional[MerchantApplication]:
        """
        获取申请对象（内部使用）

        Args:
            application_id: 申请ID

        Returns:
            Optional[MerchantApplication]: 申请对象或None
        """
        query = select(MerchantApplication).where(
            MerchantApplication.id == application_id
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _create_merchant_account(
        self, application: MerchantApplication
    ):
        """
        创建商家账户（私有方法，审核通过时调用）

        Args:
            application: 商家申请对象
        """
        from src.services.merchant_service import MerchantService

        merchant_service = MerchantService(self.db)
        await merchant_service.create_merchant_account(application)