"""
初始化脚本 - 创建默认管理员账户
运行方式: python -m src.scripts.init_admin
"""
import asyncio
import sys
from uuid import uuid4

from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.core.security import hash_password
from src.models.admin import AdminUser


async def create_default_admin():
    """创建默认管理员账户"""

    # 默认管理员配置
    DEFAULT_ADMIN = {
        "username": "admin",
        "password": "admin123",  # 生产环境请修改
        "name": "系统管理员",
        "email": "admin@grainadmin.local",
        "is_active": True,
    }

    async with AsyncSessionLocal() as session:
        # 检查管理员是否已存在
        stmt = select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN["username"])
        result = await session.execute(stmt)
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print(f"✅ 管理员账户 '{DEFAULT_ADMIN['username']}' 已存在，跳过创建")
            print(f"   ID: {existing_admin.id}")
            print(f"   姓名: {existing_admin.name}")
            print(f"   邮箱: {existing_admin.email}")
            return

        # 创建新管理员
        admin = AdminUser(
            id=uuid4(),
            username=DEFAULT_ADMIN["username"],
            password_hash=hash_password(DEFAULT_ADMIN["password"]),
            name=DEFAULT_ADMIN["name"],
            email=DEFAULT_ADMIN["email"],
            is_active=DEFAULT_ADMIN["is_active"],
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print("✅ 默认管理员账户创建成功！")
        print(f"   用户名: {admin.username}")
        print(f"   密码: {DEFAULT_ADMIN['password']}")
        print(f"   姓名: {admin.name}")
        print(f"   邮箱: {admin.email}")
        print(f"   ID: {admin.id}")
        print("\n⚠️  请在生产环境中修改默认密码！")


async def main():
    """主函数"""
    try:
        await create_default_admin()
    except Exception as e:
        print(f"❌ 创建管理员失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())