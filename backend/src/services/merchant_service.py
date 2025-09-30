"""
商家账户服务层
包含账户创建、查询、更新，并集成 Redis 缓存
"""
import json
import secrets
import string
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import redis_manager
from src.models.enums import MerchantLevel, MerchantStatus
from src.models.merchant_application import MerchantApplication
from src.models.merchant_account import MerchantAccount
from src.schemas.merchant import UpdateMerchantRequest


class MerchantService:
    """商家账户服务（带 Redis 缓存）"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_ttl = 3600  # 缓存 TTL：1小时

    async def create_merchant_account(
        self, application: MerchantApplication
    ) -> MerchantAccount:
        """
        创建商家账户（审核通过后自动调用）

        Args:
            application: 商家申请对象

        Returns:
            MerchantAccount: 创建的商家账户

        Raises:
            ValueError: 申请不存在或已有账户
        """
        # 检查是否已存在账户
        existing = await self._get_account_by_application_id(application.id)
        if existing:
            raise ValueError("该申请已创建商家账户")

        # 生成商家编号
        merchant_id = await self.generate_merchant_id()

        # 生成随机密码
        password = self.generate_random_password()

        # 创建账户
        account = MerchantAccount(
            merchant_id=merchant_id,
            username=application.contact_phone,  # 默认使用联系电话作为用户名
            level=MerchantLevel.NORMAL,
            status=MerchantStatus.ACTIVE,
            application_id=application.id,
        )
        account.set_password(password)

        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        # TODO: 发送登录凭证到商家邮箱/短信（未来功能）
        # await self._send_credentials(application.contact_email, merchant_id, password)

        return account

    async def generate_merchant_id(self) -> str:
        """
        生成商家编号（格式：M + YYYYMMDD + 序号）

        Returns:
            str: 商家编号（如 M20250930001）
        """
        # 获取今天日期
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"M{today}"

        # 查询今天已生成的最大序号
        query = select(func.max(MerchantAccount.merchant_id)).where(
            MerchantAccount.merchant_id.like(f"{prefix}%")
        )
        result = await self.db.execute(query)
        max_merchant_id = result.scalar_one_or_none()

        # 生成新序号
        if max_merchant_id:
            # 提取序号并加1
            current_seq = int(max_merchant_id[-3:])
            new_seq = current_seq + 1
        else:
            # 今天第一个商家
            new_seq = 1

        # 格式化为3位序号
        merchant_id = f"{prefix}{new_seq:03d}"

        return merchant_id

    def generate_random_password(self, length: int = 8) -> str:
        """
        生成随机密码

        Args:
            length: 密码长度（默认8位）

        Returns:
            str: 随机密码
        """
        # 包含大小写字母和数字
        characters = string.ascii_letters + string.digits
        password = "".join(secrets.choice(characters) for _ in range(length))

        return password

    async def get_merchant(
        self, merchant_id: str
    ) -> Optional[MerchantAccount]:
        """
        根据商家编号获取商家账户（带缓存）

        Args:
            merchant_id: 商家编号

        Returns:
            Optional[MerchantAccount]: 商家账户或None
        """
        # 1. 尝试从缓存获取
        cached_merchant = await self._get_merchant_from_cache(merchant_id)
        if cached_merchant:
            return cached_merchant

        # 2. 缓存未命中，从数据库查询
        query = select(MerchantAccount).where(
            MerchantAccount.merchant_id == merchant_id
        )

        result = await self.db.execute(query)
        merchant = result.scalar_one_or_none()

        # 3. 如果找到，写入缓存
        if merchant:
            await self._set_merchant_cache(merchant)

        return merchant

    async def get_merchant_by_id(self, id: UUID) -> Optional[MerchantAccount]:
        """
        根据主键ID获取商家账户

        Args:
            id: 商家账户主键ID

        Returns:
            Optional[MerchantAccount]: 商家账户或None
        """
        query = select(MerchantAccount).where(MerchantAccount.id == id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_merchant_by_username(
        self, username: str
    ) -> Optional[MerchantAccount]:
        """
        根据用户名获取商家账户（用于登录）

        Args:
            username: 用户名

        Returns:
            Optional[MerchantAccount]: 商家账户或None
        """
        query = select(MerchantAccount).where(
            MerchantAccount.username == username
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_merchant(
        self, merchant_id: str, data: UpdateMerchantRequest
    ) -> Optional[MerchantAccount]:
        """
        更新商家信息（仅允许更新部分字段）- Write-through 缓存失效

        Args:
            merchant_id: 商家编号
            data: 更新数据

        Returns:
            Optional[MerchantAccount]: 更新后的商家账户或None
        """
        account = await self.get_merchant(merchant_id)
        if not account:
            return None

        # 更新关联的申请信息（联系方式）
        if account.application:
            if data.contact_phone:
                account.application.contact_phone = data.contact_phone
                # 更新用户名（使用新的联系电话）
                account.username = data.contact_phone

            if data.contact_email:
                account.application.contact_email = data.contact_email

        await self.db.commit()
        await self.db.refresh(account)

        # 失效缓存（Write-through）
        await self._invalidate_merchant_cache(merchant_id)

        return account

    async def change_merchant_status(
        self, merchant_id: str, status: MerchantStatus
    ) -> Optional[MerchantAccount]:
        """
        变更商家账户状态（冻结/注销/恢复）

        Args:
            merchant_id: 商家编号
            status: 目标状态

        Returns:
            Optional[MerchantAccount]: 更新后的商家账户或None
        """
        account = await self.get_merchant(merchant_id)
        if not account:
            return None

        account.status = status
        await self.db.commit()
        await self.db.refresh(account)

        # 失效缓存
        await self._invalidate_merchant_cache(merchant_id)

        return account

    async def change_password(
        self, merchant_id: str, old_password: str, new_password: str
    ) -> bool:
        """
        修改密码

        Args:
            merchant_id: 商家编号
            old_password: 旧密码
            new_password: 新密码

        Returns:
            bool: 是否修改成功

        Raises:
            ValueError: 旧密码错误
        """
        account = await self.get_merchant(merchant_id)
        if not account:
            return False

        # 验证旧密码
        if not account.verify_password(old_password):
            raise ValueError("旧密码错误")

        # 设置新密码
        account.set_password(new_password)
        await self.db.commit()

        return True

    async def _get_account_by_application_id(
        self, application_id: UUID
    ) -> Optional[MerchantAccount]:
        """
        根据申请ID获取商家账户（内部使用）

        Args:
            application_id: 申请ID

        Returns:
            Optional[MerchantAccount]: 商家账户或None
        """
        query = select(MerchantAccount).where(
            MerchantAccount.application_id == application_id
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _send_credentials(
        self, email: str, merchant_id: str, password: str
    ):
        """
        发送登录凭证到商家邮箱（未来功能）

        Args:
            email: 商家邮箱
            merchant_id: 商家编号
            password: 初始密码
        """
        # TODO: 集成邮件服务发送登录凭证
        pass

    # ========================================
    # Redis 缓存方法
    # ========================================

    def _get_cache_key(self, merchant_id: str) -> str:
        """生成缓存键"""
        return f"merchant:{merchant_id}"

    async def _get_merchant_from_cache(
        self, merchant_id: str
    ) -> Optional[MerchantAccount]:
        """
        从 Redis 缓存获取商家信息

        Args:
            merchant_id: 商家编号

        Returns:
            Optional[MerchantAccount]: 商家账户或None（缓存未命中）
        """
        cache_key = self._get_cache_key(merchant_id)

        try:
            cached_data = await redis_manager.get_json(cache_key)
            if cached_data:
                print(f"✅ 缓存命中: {cache_key}")
                # 将字典转换回 MerchantAccount 对象
                # 注意: 这里简化处理，实际应该更严格
                account = MerchantAccount(**cached_data)
                return account
        except Exception as e:
            print(f"⚠️  缓存读取失败: {cache_key}, 错误: {e}")

        print(f"❌ 缓存未命中: {cache_key}")
        return None

    async def _set_merchant_cache(self, merchant: MerchantAccount) -> None:
        """
        将商家信息写入 Redis 缓存

        Args:
            merchant: 商家账户对象
        """
        cache_key = self._get_cache_key(merchant.merchant_id)

        try:
            # 将对象转换为字典（排除敏感字段）
            merchant_dict = merchant.to_dict()
            await redis_manager.set_json(cache_key, merchant_dict, ttl=self.cache_ttl)
            print(f"✅ 缓存设置成功: {cache_key}, TTL={self.cache_ttl}s")
        except Exception as e:
            print(f"⚠️  缓存设置失败: {cache_key}, 错误: {e}")

    async def _invalidate_merchant_cache(self, merchant_id: str) -> None:
        """
        失效商家缓存

        Args:
            merchant_id: 商家编号
        """
        cache_key = self._get_cache_key(merchant_id)

        try:
            await redis_manager.delete(cache_key)
            print(f"✅ 缓存失效: {cache_key}")
        except Exception as e:
            print(f"⚠️  缓存失效失败: {cache_key}, 错误: {e}")