"""
JWT 黑名单功能测试
测试 token 登出和黑名单功能
"""
import pytest
from uuid import uuid4

from src.core.redis import redis_manager
from src.core.security import (
    create_access_token,
    verify_token,
    add_token_to_blacklist,
    is_token_blacklisted,
)


async def ensure_redis():
    """确保 Redis 已连接"""
    if redis_manager._redis is None:
        await redis_manager.connect()


@pytest.mark.asyncio
async def test_jwt_has_jti():
    """测试 JWT token 包含 jti 字段"""
    await ensure_redis()

    user_id = uuid4()
    token = create_access_token(user_id=user_id, user_role="admin")

    payload = await verify_token(token)

    assert payload is not None
    assert "jti" in payload
    assert payload["jti"] is not None


@pytest.mark.asyncio
async def test_token_blacklist():
    """测试 token 黑名单功能"""
    await ensure_redis()

    user_id = uuid4()
    token = create_access_token(user_id=user_id, user_role="admin")

    # 1. 验证 token 有效
    payload = await verify_token(token)
    assert payload is not None

    # 2. 将 token 加入黑名单
    jti = payload["jti"]
    await add_token_to_blacklist(jti, expires_in=3600)

    # 3. 检查 token 是否在黑名单中
    is_blacklisted = await is_token_blacklisted(jti)
    assert is_blacklisted is True

    # 4. 再次验证 token 应该失败（因为在黑名单中）
    payload_after_blacklist = await verify_token(token)
    assert payload_after_blacklist is None


@pytest.mark.asyncio
async def test_non_blacklisted_token():
    """测试未加入黑名单的 token 正常工作"""
    await ensure_redis()

    user_id = uuid4()
    token = create_access_token(user_id=user_id, user_role="merchant", merchant_id="M20250930001")

    # 验证 token
    payload = await verify_token(token)

    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "merchant"
    assert payload["merchant_id"] == "M20250930001"
    assert "jti" in payload

    # 检查是否在黑名单中（应该不在）
    jti = payload["jti"]
    is_blacklisted = await is_token_blacklisted(jti)
    assert is_blacklisted is False


@pytest.mark.asyncio
async def test_refresh_token_not_checked_for_blacklist():
    """测试 refresh token 不会被黑名单检查"""
    await ensure_redis()

    from src.core.security import create_refresh_token

    user_id = uuid4()
    refresh_token = create_refresh_token(user_id=user_id)

    # refresh token 应该能正常验证（不包含 jti，不检查黑名单）
    payload = await verify_token(refresh_token, token_type="refresh")

    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"