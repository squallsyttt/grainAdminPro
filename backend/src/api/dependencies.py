"""
API 依赖注入
提供数据库会话、当前用户等通用依赖项
"""
from typing import AsyncGenerator, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token


# HTTP Bearer Token 安全方案（用于JWT认证）
security = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话

    使用方式:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async for session in get_db():
        yield session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    获取当前登录用户（从JWT Token中解析）

    Returns:
        dict: 用户信息字典
            - user_id: UUID
            - role: str (admin/merchant)
            - merchant_id: Optional[str]
            - name: Optional[str]

    Raises:
        HTTPException: 401 Unauthorized (Token无效或过期)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 验证 JWT Token
    payload = await verify_token(token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从 payload 提取用户信息
    user_info = {
        "user_id": payload["sub"],
        "role": payload["role"],
        "merchant_id": payload.get("merchant_id"),
        "name": payload.get("name"),
    }

    return user_info


async def get_current_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    获取当前管理员用户（仅管理员可访问）

    Returns:
        dict: 管理员用户信息

    Raises:
        HTTPException: 403 Forbidden (非管理员用户)
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


async def get_current_merchant(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    获取当前商家用户（仅商家可访问）

    Returns:
        dict: 商家用户信息

    Raises:
        HTTPException: 403 Forbidden (非商家用户)
    """
    if current_user["role"] != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要商家权限",
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    获取可选的当前用户（不强制要求认证）

    Returns:
        Optional[dict]: 用户信息或None

    Note:
        用于公开API端点，但需要区分已登录和未登录状态
        注意：此函数为同步函数，不检查JWT黑名单
    """
    if not credentials:
        return None

    token = credentials.credentials

    # 使用 decode_token_payload 替代 verify_token（同步版本，不检查黑名单）
    from src.core.security import decode_token_payload
    payload = decode_token_payload(token)

    if not payload:
        return None

    return {
        "user_id": payload["sub"],
        "role": payload["role"],
        "merchant_id": payload.get("merchant_id"),
        "name": payload.get("name"),
    }


# ==================== RBAC 权限控制 ====================


def require_roles(allowed_roles: List[str]):
    """
    装饰器工厂：要求用户具有指定角色之一

    Args:
        allowed_roles: 允许的角色列表，如 ["admin", "merchant"]

    Returns:
        Depends: FastAPI 依赖函数

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: dict = Depends(require_roles(["admin"]))
        ):
            ...
    """

    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        """检查用户角色是否在允许列表中"""
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(allowed_roles)}",
            )
        return current_user

    return Depends(role_checker)


async def check_resource_ownership(
    current_user: dict,
    resource_owner_id: Optional[UUID],
    db: AsyncSession,
) -> bool:
    """
    检查用户是否拥有资源访问权限

    权限规则:
    - 管理员：可访问所有资源
    - 商家：只能访问自己的资源

    Args:
        current_user: 当前用户信息（from get_current_user）
        resource_owner_id: 资源所有者的用户 ID
        db: 数据库会话

    Returns:
        bool: True 表示有权限，False 表示无权限

    Usage:
        if not await check_resource_ownership(current_user, application.id, db):
            raise HTTPException(status_code=403, detail="无权访问此资源")
    """
    # 管理员可以访问所有资源
    if current_user["role"] == "admin":
        return True

    # 商家只能访问自己的资源
    if current_user["role"] == "merchant":
        user_id = UUID(current_user["user_id"])

        # 如果资源没有所有者（如公开资源），拒绝访问
        if resource_owner_id is None:
            return False

        # 检查资源是否属于当前商家
        return user_id == resource_owner_id

    # 其他未知角色，拒绝访问
    return False


async def check_merchant_application_access(
    current_user: dict,
    application_id: UUID,
    db: AsyncSession,
) -> bool:
    """
    检查用户是否有权访问指定的商家申请

    Args:
        current_user: 当前用户
        application_id: 申请 ID
        db: 数据库会话

    Returns:
        bool: 是否有权限
    """
    # 管理员可访问所有申请
    if current_user["role"] == "admin":
        return True

    # 商家只能访问自己的申请
    if current_user["role"] == "merchant":
        from src.models.merchant_account import MerchantAccount
        from src.models.merchant_application import MerchantApplication

        # 查询申请是否属于当前商家
        stmt = (
            select(MerchantApplication)
            .join(MerchantAccount, MerchantAccount.application_id == MerchantApplication.id)
            .where(
                MerchantApplication.id == application_id,
                MerchantAccount.id == UUID(current_user["user_id"]),
            )
        )

        result = await db.execute(stmt)
        application = result.scalar_one_or_none()

        return application is not None

    return False