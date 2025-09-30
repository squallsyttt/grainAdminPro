"""
认证服务
处理用户登录、token 生成和验证等
"""
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.security import create_access_token, create_refresh_token, verify_password, verify_token
from src.models.admin import AdminUser
from src.models.enums import MerchantStatus
from src.models.merchant_account import MerchantAccount


class AuthService:
    """认证服务类"""

    def __init__(self, db: AsyncSession):
        """
        初始化认证服务

        Args:
            db: 数据库会话
        """
        self.db = db

    async def authenticate_user(self, username: str, password: str) -> Optional[Tuple[str, dict]]:
        """
        验证用户登录凭证

        支持两种用户登录：
        1. 管理员用户（username + password）
        2. 商家用户（merchant_id + password）

        Args:
            username: 用户名或商家编号
            password: 密码

        Returns:
            Tuple[str, dict] | None: (user_role, user_info) 或 None
            - user_role: "admin" | "merchant"
            - user_info: 用户信息字典

        Example:
            ```python
            result = await auth_service.authenticate_user("admin", "password123")
            if result:
                role, info = result
                print(f"User {info['name']} logged in as {role}")
            ```
        """
        # 1. 尝试作为管理员登录
        admin_stmt = select(AdminUser).where(
            or_(AdminUser.username == username, AdminUser.email == username)
        )
        admin_result = await self.db.execute(admin_stmt)
        admin = admin_result.scalar_one_or_none()

        if admin and admin.is_active:
            # 验证密码
            if verify_password(password, admin.password_hash):
                return (
                    "admin",
                    {
                        "user_id": admin.id,
                        "username": admin.username,
                        "name": admin.name,
                        "email": admin.email,
                    },
                )

        # 2. 尝试作为商家登录
        merchant_stmt = (
            select(MerchantAccount)
            .where(
                or_(
                    MerchantAccount.merchant_id == username,
                    MerchantAccount.username == username,
                )
            )
            .options(selectinload(MerchantAccount.application))
        )
        merchant_result = await self.db.execute(merchant_stmt)
        merchant = merchant_result.scalar_one_or_none()

        if merchant and merchant.status == MerchantStatus.ACTIVE:
            # 验证密码
            if verify_password(password, merchant.password_hash):
                return (
                    "merchant",
                    {
                        "user_id": merchant.id,
                        "merchant_id": merchant.merchant_id,
                        "name": merchant.application.business_name,
                        "email": merchant.application.contact_email,
                    },
                )

        # 用户不存在或密码错误
        return None

    def generate_tokens(self, user_id: UUID, role: str, merchant_id: Optional[str] = None) -> dict:
        """
        生成访问令牌和刷新令牌

        Args:
            user_id: 用户ID
            role: 用户角色（admin/merchant）
            merchant_id: 商家编号（仅商家用户需要）

        Returns:
            dict: Token信息
                - access_token: 访问令牌（15分钟有效期）
                - refresh_token: 刷新令牌（7天有效期）
                - token_type: "bearer"
                - expires_in: 900（秒）
        """
        access_token = create_access_token(
            user_id=user_id,
            user_role=role,
            merchant_id=merchant_id,
        )

        refresh_token = create_refresh_token(user_id=user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转换为秒
        }

    async def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        """
        使用刷新令牌换取新的访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            dict | None: 新的 token 信息，验证失败返回 None
        """
        # 验证 refresh token
        payload = await verify_token(refresh_token, token_type="refresh")

        if not payload:
            return None

        user_id_str = payload["sub"]
        user_id = UUID(user_id_str)

        # 查询用户信息以获取最新的 role 和 merchant_id
        # 1. 先尝试查询管理员
        admin_stmt = select(AdminUser).where(AdminUser.id == user_id)
        admin_result = await self.db.execute(admin_stmt)
        admin = admin_result.scalar_one_or_none()

        if admin and admin.is_active:
            return self.generate_tokens(user_id=user_id, role="admin")

        # 2. 尝试查询商家
        merchant_stmt = (
            select(MerchantAccount)
            .where(MerchantAccount.id == user_id)
            .options(selectinload(MerchantAccount.application))
        )
        merchant_result = await self.db.execute(merchant_stmt)
        merchant = merchant_result.scalar_one_or_none()

        if merchant and merchant.status == MerchantStatus.ACTIVE:
            return self.generate_tokens(
                user_id=user_id,
                role="merchant",
                merchant_id=merchant.merchant_id,
            )

        # 用户不存在或已禁用
        return None

    async def get_user_info(self, user_id: UUID, role: str) -> Optional[dict]:
        """
        获取用户详细信息

        Args:
            user_id: 用户ID
            role: 用户角色（admin/merchant）

        Returns:
            dict | None: 用户信息
        """
        if role == "admin":
            stmt = select(AdminUser).where(AdminUser.id == user_id)
            result = await self.db.execute(stmt)
            admin = result.scalar_one_or_none()

            if admin:
                return {
                    "user_id": str(admin.id),
                    "username": admin.username,
                    "role": "admin",
                    "merchant_id": None,
                    "merchant_name": None,
                }

        elif role == "merchant":
            stmt = (
                select(MerchantAccount)
                .where(MerchantAccount.id == user_id)
                .options(selectinload(MerchantAccount.application))
            )
            result = await self.db.execute(stmt)
            merchant = result.scalar_one_or_none()

            if merchant:
                return {
                    "user_id": str(merchant.id),
                    "username": None,
                    "role": "merchant",
                    "merchant_id": merchant.merchant_id,
                    "merchant_name": merchant.application.business_name,
                }

        return None