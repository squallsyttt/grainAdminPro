"""
商家账户 API 端点
处理商家账户信息查询和更新
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user
from src.schemas.merchant import MerchantResponse, UpdateMerchantRequest
from src.services.merchant_service import MerchantService


router = APIRouter()


@router.get(
    "/{merchant_id}",
    response_model=MerchantResponse,
    summary="查询商家信息",
    description="根据商家编号查询商家账户信息",
)
async def get_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> MerchantResponse:
    """
    查询商家信息

    **权限**:
    - 管理员: 可查询所有商家信息
    - 商家: 仅可查询自己的信息（TODO: 实现权限验证）

    **参数**:
    - merchant_id: 商家编号（如 M20250930001）

    **返回**:
    商家账户信息（不包含密码哈希）
    """
    service = MerchantService(db)

    try:
        # TODO: 权限验证
        # if current_user["role"] == "merchant":
        #     if current_user["merchant_id"] != merchant_id:
        #         raise HTTPException(
        #             status_code=status.HTTP_403_FORBIDDEN,
        #             detail="无权查询其他商家的信息",
        #         )

        merchant = await service.get_merchant(merchant_id)

        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家不存在",
            )

        return MerchantResponse.model_validate(merchant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询商家信息失败: {str(e)}",
        )


@router.patch(
    "/{merchant_id}",
    response_model=MerchantResponse,
    summary="更新商家信息",
    description="更新商家账户信息（仅允许更新部分字段）",
)
async def update_merchant(
    merchant_id: str,
    data: UpdateMerchantRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
) -> MerchantResponse:
    """
    更新商家信息

    **权限**:
    - 管理员: 可更新所有商家信息
    - 商家: 仅可更新自己的信息（TODO: 实现权限验证）

    **可更新字段**:
    - contact_phone: 联系电话
    - contact_email: 联系邮箱

    **参数**:
    - merchant_id: 商家编号
    """
    service = MerchantService(db)

    try:
        # TODO: 权限验证
        # if current_user["role"] == "merchant":
        #     if current_user["merchant_id"] != merchant_id:
        #         raise HTTPException(
        #             status_code=status.HTTP_403_FORBIDDEN,
        #             detail="无权更新其他商家的信息",
        #         )

        merchant = await service.update_merchant(merchant_id, data)

        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家不存在",
            )

        return MerchantResponse.model_validate(merchant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新商家信息失败: {str(e)}",
        )