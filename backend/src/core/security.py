"""
安全模块 - JWT 认证与密码哈希
提供 JWT token 生成/验证、密码加密等安全功能
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.redis import redis_manager

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    使用 bcrypt 对密码进行哈希加密

    Args:
        password: 明文密码

    Returns:
        str: 加密后的密码哈希值
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID,
    user_role: str,
    merchant_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建访问令牌（Access Token）

    Args:
        user_id: 用户 ID
        user_role: 用户角色（admin/merchant）
        merchant_id: 商家编号（仅商家用户需要）
        expires_delta: 过期时间增量（默认 15 分钟）

    Returns:
        str: JWT access token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta
    jti = str(uuid.uuid4())  # JWT ID - 用于黑名单

    to_encode = {
        "sub": str(user_id),  # subject: 用户 ID
        "role": user_role,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),  # issued at
        "jti": jti,  # JWT ID
    }

    # 商家用户需要包含 merchant_id
    if merchant_id:
        to_encode["merchant_id"] = merchant_id

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def create_refresh_token(
    user_id: UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建刷新令牌（Refresh Token）

    Args:
        user_id: 用户 ID
        expires_delta: 过期时间增量（默认 7 天）

    Returns:
        str: JWT refresh token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


async def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    验证 JWT token 并解析 payload（包含黑名单检查）

    Args:
        token: JWT token 字符串
        token_type: token 类型（access/refresh）

    Returns:
        dict | None: token payload，验证失败返回 None

    Payload 结构:
        {
            "sub": "user_id",
            "role": "admin" | "merchant",
            "merchant_id": "M20250930001",  # 仅商家用户
            "type": "access" | "refresh",
            "exp": 1234567890,
            "iat": 1234567890,
            "jti": "uuid"  # JWT ID - 用于黑名单
        }
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # 验证 token 类型
        if payload.get("type") != token_type:
            return None

        # 验证必需字段
        if not payload.get("sub"):
            return None

        # 检查黑名单（仅对 access token）
        if token_type == "access":
            jti = payload.get("jti")
            if jti and await is_token_blacklisted(jti):
                return None  # Token 已被加入黑名单

        return payload

    except JWTError:
        return None


def decode_token_payload(token: str) -> Optional[dict]:
    """
    解码 token payload（不验证签名，仅用于调试）

    Args:
        token: JWT token 字符串

    Returns:
        dict | None: token payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False},
        )
        return payload
    except JWTError:
        return None


async def add_token_to_blacklist(jti: str, expires_in: int) -> None:
    """
    添加 token 到黑名单

    Args:
        jti: JWT ID
        expires_in: token 剩余有效期（秒）
    """
    cache_key = f"jwt_blacklist:{jti}"
    await redis_manager.set(cache_key, "1", ttl=expires_in)


async def is_token_blacklisted(jti: str) -> bool:
    """
    检查 token 是否在黑名单中

    Args:
        jti: JWT ID

    Returns:
        bool: 是否在黑名单中
    """
    cache_key = f"jwt_blacklist:{jti}"
    return await redis_manager.exists(cache_key)