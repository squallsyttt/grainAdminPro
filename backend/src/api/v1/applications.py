"""
商家申请 API 端点
处理商家入驻申请的 CRUD 操作
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user, get_current_admin
from src.schemas.application import (
    CreateApplicationRequest,
    UpdateApplicationRequest,
    ApplicationResponse,
    ApplicationDetailResponse,
    ApplicationListResponse,
)
from src.services.application_service import ApplicationService


router = APIRouter()


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建商家申请",
    description="创建新的商家入驻申请（草稿状态）",
)
async def create_application(
    data: CreateApplicationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> ApplicationResponse:
    """
    创建商家申请

    - **business_name**: 企业名称
    - **unified_social_credit**: 统一社会信用代码（18位）
    - **legal_person_name**: 法人姓名
    - **legal_person_id_number**: 法人身份证号（18位）
    - **contact_name**: 联系人姓名
    - **contact_phone**: 联系电话（11位手机号）
    - **contact_email**: 联系邮箱
    - **business_categories**: 经营类目（数组，至少1个）

    返回创建的申请对象（status=DRAFT）
    """
    service = ApplicationService(db)

    try:
        application = await service.create_application(data)
        return ApplicationResponse.model_validate(application)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建申请失败: {str(e)}",
        )


@router.get(
    "",
    response_model=ApplicationListResponse,
    summary="查询申请列表",
    description="查询商家申请列表（支持分页和筛选）",
)
async def list_applications(
    status_filter: Optional[str] = Query(
        None, alias="status", description="按状态筛选（draft/pending/under_review/approved/rejected/require_supplement）"
    ),
    business_name: Optional[str] = Query(
        None, description="按企业名称模糊搜索"
    ),
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量（1-100）"),
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> ApplicationListResponse:
    """
    查询申请列表

    **权限**:
    - 管理员: 可查询所有申请
    - 商家: 仅可查询自己的申请（TODO: 实现权限过滤）

    **筛选条件**:
    - status: 申请状态
    - business_name: 企业名称（模糊搜索）

    **分页**:
    - page: 页码（从1开始）
    - page_size: 每页数量（默认20，最大100）
    """
    service = ApplicationService(db)

    # 构建筛选条件
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    if business_name:
        filters["business_name"] = business_name

    # TODO: 商家用户过滤（仅查询自己的申请）
    # if current_user["role"] == "merchant":
    #     filters["merchant_id"] = current_user["merchant_id"]

    try:
        applications, total = await service.list_applications(
            filters=filters,
            page=page,
            page_size=page_size,
        )

        return ApplicationListResponse(
            items=[ApplicationResponse.model_validate(app) for app in applications],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询申请列表失败: {str(e)}",
        )


@router.get(
    "/{application_id}",
    response_model=ApplicationDetailResponse,
    summary="查询申请详情",
    description="根据ID查询商家申请详细信息",
)
async def get_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> ApplicationDetailResponse:
    """
    查询申请详情

    **权限**:
    - 管理员: 可查询所有申请
    - 商家: 仅可查询自己的申请（TODO: 实现权限验证）
    """
    service = ApplicationService(db)

    try:
        application = await service.get_application(
            application_id,
            user_role=current_user["role"],
            user_id=current_user.get("user_id"),
        )

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请不存在",
            )

        return ApplicationDetailResponse.model_validate(application)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询申请详情失败: {str(e)}",
        )


@router.put(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="更新申请信息",
    description="更新商家申请信息（仅草稿和待补充状态可修改）",
)
async def update_application(
    application_id: UUID,
    data: UpdateApplicationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> ApplicationResponse:
    """
    更新申请信息

    **允许更新的状态**: DRAFT、REQUIRE_SUPPLEMENT

    **权限**:
    - 管理员: 可更新所有申请
    - 商家: 仅可更新自己的申请（TODO: 实现权限验证）
    """
    service = ApplicationService(db)

    try:
        application = await service.update_application(application_id, data)

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请不存在",
            )

        return ApplicationResponse.model_validate(application)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新申请失败: {str(e)}",
        )


@router.post(
    "/{application_id}/submit",
    response_model=ApplicationResponse,
    summary="提交申请",
    description="提交商家申请（从草稿或待补充状态变更为待审核）",
)
async def submit_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> ApplicationResponse:
    """
    提交申请

    **状态转换**:
    - DRAFT → PENDING
    - REQUIRE_SUPPLEMENT → PENDING

    **验证**:
    - 所有必填字段完整
    - 必需文件已上传（营业执照、身份证正反面）

    **权限**:
    - 管理员: 可提交所有申请
    - 商家: 仅可提交自己的申请（TODO: 实现权限验证）
    """
    service = ApplicationService(db)

    try:
        application = await service.submit_application(application_id)
        return ApplicationResponse.model_validate(application)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交申请失败: {str(e)}",
        )