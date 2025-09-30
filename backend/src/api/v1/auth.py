"""
认证 API 端点
处理登录、token 刷新、用户信息查询等
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserInfoResponse,
)
from src.services.auth_service import AuthService
from src.services.merchant_service import MerchantService

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="用户登录",
    description="管理员和商家统一登录入口",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """
    用户登录

    **支持两种用户登录**:
    1. 管理员: 使用 username 或 email + password
    2. 商家: 使用 merchant_id 或 email + password

    **参数**:
    - username: 用户名/商家编号/邮箱
    - password: 密码

    **返回**:
    - access_token: 访问令牌（15分钟有效期）
    - refresh_token: 刷新令牌（7天有效期）
    - token_type: "bearer"
    - expires_in: 900（秒）

    **错误**:
    - 401: 用户名或密码错误
    """
    service = AuthService(db)

    # 验证用户凭证
    auth_result = await service.authenticate_user(data.username, data.password)

    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    role, user_info = auth_result

    # 生成 tokens
    merchant_id = user_info.get("merchant_id") if role == "merchant" else None
    tokens = service.generate_tokens(
        user_id=user_info["user_id"],
        role=role,
        merchant_id=merchant_id,
    )

    return TokenResponse(**tokens)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="刷新访问令牌",
    description="使用刷新令牌换取新的访问令牌",
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """
    刷新访问令牌

    使用 refresh_token 换取新的 access_token

    **参数**:
    - refresh_token: 刷新令牌

    **返回**:
    - 新的访问令牌和刷新令牌

    **错误**:
    - 401: 刷新令牌无效或已过期
    """
    service = AuthService(db)

    # 刷新 token
    tokens = await service.refresh_access_token(data.refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的刷新令牌",
        )

    return TokenResponse(**tokens)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="用户登出",
    description="退出登录（将 token 加入黑名单，客户端需清除本地 token）",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    """
    用户登出

    实现服务端真正的登出：
    - 将当前 access token 的 jti 加入黑名单（Redis）
    - 客户端仍需清除本地存储的 token

    **返回**:
    - 成功消息
    """
    from datetime import datetime
    from jose import jwt
    from src.core.config import settings
    from src.core.security import add_token_to_blacklist

    # 解析 token 获取 jti 和过期时间
    token = credentials.credentials
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    jti = payload.get("jti")
    exp = payload.get("exp")

    if jti and exp:
        # 计算 token 剩余有效期
        expires_in = exp - int(datetime.utcnow().timestamp())
        if expires_in > 0:
            # 将 token 加入黑名单
            await add_token_to_blacklist(jti, expires_in)

    return MessageResponse(message="登出成功，token 已失效")


@router.get(
    "/me",
    response_model=UserInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息",
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> UserInfoResponse:
    """
    获取当前用户信息

    **返回**:
    - user_id: 用户ID
    - username: 用户名（仅管理员）
    - role: 用户角色（admin/merchant）
    - merchant_id: 商家编号（仅商家）
    - merchant_name: 商家名称（仅商家）

    **权限**:
    - 需要有效的 access_token
    """
    service = AuthService(db)

    user_id = UUID(current_user["user_id"])
    role = current_user["role"]

    user_info = await service.get_user_info(user_id, role)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    return UserInfoResponse(**user_info)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="修改密码",
    description="商家修改自己的密码",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """
    修改密码

    **权限**:
    - 仅商家用户可修改自己的密码
    - 管理员密码修改需通过其他安全途径

    **参数**:
    - old_password: 旧密码
    - new_password: 新密码（至少6位）

    **返回**:
    - 成功消息

    **错误**:
    - 403: 非商家用户
    - 401: 旧密码错误
    """
    # 仅允许商家修改密码
    if current_user["role"] != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅商家用户可修改密码",
        )

    merchant_id = current_user["merchant_id"]
    service = MerchantService(db)

    # 修改密码
    success = await service.change_password(
        merchant_id,
        data.old_password,
        data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="旧密码错误",
        )

    return MessageResponse(message="密码修改成功，请使用新密码重新登录")