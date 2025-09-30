"""
测试配置文件
提供测试数据库和客户端 fixture
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.database import get_db
from src.main import app
from src.models import Base

# 测试数据库 URL（使用独立的测试数据库）
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "grainadmin_dev", "grainadmin_test"
).replace("postgresql://", "postgresql+asyncpg://")

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,  # 测试时不打印 SQL
    pool_pre_ping=True,
)

# 创建测试会话工厂
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环，供所有异步测试使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    创建测试数据库 fixture
    每个测试函数执行前创建表，执行后删除表
    """
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async with TestSessionLocal() as session:
        yield session

    # 清理：删除所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试客户端 fixture
    覆盖应用的数据库依赖，使用测试数据库
    """
    from src.api.dependencies import get_db_session

    # 覆盖数据库依赖 - 每个请求使用新的 session
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    # 同时覆盖 get_db 和 get_db_session
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db

    # 创建异步客户端
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    """
    创建管理员令牌 fixture
    用于需要管理员权限的测试
    """
    # 登录管理员账户（需要先在测试数据库中创建）
    from src.core.security import hash_password
    from src.models.admin import AdminUser
    from uuid import uuid4

    # 直接访问测试数据库创建管理员
    async with TestSessionLocal() as session:
        admin = AdminUser(
            id=uuid4(),
            username="test_admin",
            password_hash=hash_password("admin123"),
            name="测试管理员",
            email="test_admin@example.com",
            is_active=True,
        )
        session.add(admin)
        await session.commit()

    # 登录获取令牌
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def merchant_token(client: AsyncClient, test_db: AsyncSession) -> str:
    """
    创建商家令牌 fixture
    用于需要商家权限的测试
    """
    from src.models.merchant_account import MerchantAccount
    from src.models.merchant_application import MerchantApplication
    from src.core.security import hash_password
    from src.models.enums import ApplicationStatus
    from uuid import uuid4

    # 先创建一个申请（因为 merchant_account 依赖它）
    application = MerchantApplication(
        id=uuid4(),
        business_name="测试商家公司",
        unified_social_credit="91110108MA0123456X",
        legal_person_name="测试法人",
        legal_person_id_number="110101199001011234",
        contact_name="测试联系人",
        contact_phone="13800138000",
        contact_email="test_merchant@example.com",
        business_categories=["测试"],
        status=ApplicationStatus.APPROVED,
    )
    test_db.add(application)
    await test_db.flush()  # 获取 application.id

    # 创建商家账户
    merchant = MerchantAccount(
        id=uuid4(),
        merchant_id="M20250930001",
        username="test_merchant",
        password_hash=hash_password("merchant123"),
        application_id=application.id,
    )
    test_db.add(merchant)
    await test_db.commit()

    # 刷新session以确保数据已提交
    await test_db.refresh(merchant)
    await test_db.refresh(application)

    # 验证数据已经存在
    from sqlalchemy import select
    verify_stmt = select(MerchantAccount).where(MerchantAccount.username == "test_merchant")
    result = await test_db.execute(verify_stmt)
    verified_merchant = result.scalar_one_or_none()

    if not verified_merchant:
        raise RuntimeError("Merchant account was not created successfully")

    print(f"Merchant created: {verified_merchant.username}, password_hash: {verified_merchant.password_hash[:20]}...")

    # 登录获取令牌
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_merchant", "password": "merchant123"},
    )

    # 调试信息
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(f"Response: {response.text}")

    assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
    return response.json()["access_token"]