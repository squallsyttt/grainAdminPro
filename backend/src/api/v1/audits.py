"""
审核 API 端点
处理商家申请审核操作
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_admin
from src.schemas.audit import (
    CreateAuditRequest,
    AuditResponse,
    AuditHistoryResponse,
)
from src.services.audit_service import AuditService


router = APIRouter()


@router.post(
    "",
    response_model=AuditResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建审核记录",
    description="审核商家申请（开始审核/审核通过/审核拒绝/要求补充材料）",
)
async def create_audit(
    data: CreateAuditRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin),
) -> AuditResponse:
    """
    创建审核记录

    **权限**: 仅平台管理员可审核

    **审核动作**:
    - start_review: 开始审核
    - approve: 审核通过（自动创建商家账户）
    - reject: 审核拒绝（必须填写拒绝原因）
    - request_supplement: 要求补充材料（必须说明需要补充的内容）

    **参数**:
    - application_id: 申请ID
    - action: 审核动作
    - comment: 审核意见（reject和request_supplement时必填）
    """
    service = AuditService(db)

    try:
        # 根据动作调用不同的服务方法
        auditor_id = UUID(current_user["user_id"])
        auditor_name = current_user.get("name", "管理员")

        if data.action == "start_review":
            audit_record = await service.start_review(
                data.application_id,
                auditor_id,
                auditor_name,
            )
        elif data.action == "approve":
            audit_record = await service.approve_application(
                data.application_id,
                auditor_id,
                auditor_name,
                data.comment or "审核通过",
            )
        elif data.action == "reject":
            if not data.comment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="拒绝申请时必须填写拒绝原因",
                )
            audit_record = await service.reject_application(
                data.application_id,
                auditor_id,
                auditor_name,
                data.comment,
            )
        elif data.action == "request_supplement":
            if not data.comment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="要求补充材料时必须说明需要补充的内容",
                )
            audit_record = await service.request_supplement(
                data.application_id,
                auditor_id,
                auditor_name,
                data.comment,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的审核动作: {data.action}",
            )

        return AuditResponse.model_validate(audit_record)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核操作失败: {str(e)}",
        )


@router.get(
    "/history/{application_id}",
    response_model=AuditHistoryResponse,
    summary="查询审核历史",
    description="查询指定申请的审核历史记录",
)
async def get_audit_history(
    application_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin),
) -> AuditHistoryResponse:
    """
    查询审核历史

    **权限**:
    - 管理员: 可查询所有申请的审核历史
    - 商家: 可查询自己申请的审核历史（TODO: 实现权限验证）

    返回按时间倒序排列的审核记录列表
    """
    service = AuditService(db)

    try:
        records = await service.get_audit_history(application_id)

        return AuditHistoryResponse(
            application_id=application_id,
            records=[AuditResponse.model_validate(record) for record in records],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询审核历史失败: {str(e)}",
        )