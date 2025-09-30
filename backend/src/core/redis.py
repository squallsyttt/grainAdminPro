"""
Redis 连接管理模块
提供 Redis 客户端实例和缓存工具函数
"""
import json
from typing import Any, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

from src.core.config import settings


class RedisManager:
    """Redis 连接管理器"""

    def __init__(self) -> None:
        self._redis: Optional[Redis] = None

    async def connect(self) -> None:
        """建立 Redis 连接"""
        # 只有当密码不为空时才传递 password 参数
        connect_kwargs = {
            "encoding": "utf-8",
            "decode_responses": True,
        }

        if settings.REDIS_PASSWORD:
            connect_kwargs["password"] = settings.REDIS_PASSWORD

        self._redis = await aioredis.from_url(
            settings.REDIS_URL,
            **connect_kwargs
        )

    async def disconnect(self) -> None:
        """关闭 Redis 连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def get_client(self) -> Redis:
        """获取 Redis 客户端实例"""
        if not self._redis:
            raise RuntimeError("Redis 未初始化，请先调用 connect()")
        return self._redis

    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        client = self.get_client()
        return await client.get(key)

    async def set(
        self, key: str, value: str, ttl: Optional[int] = None
    ) -> None:
        """设置缓存值"""
        client = self.get_client()
        await client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        """删除缓存键"""
        client = self.get_client()
        await client.delete(key)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        client = self.get_client()
        return bool(await client.exists(key))

    async def get_json(self, key: str) -> Optional[Any]:
        """获取 JSON 格式缓存"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        """设置 JSON 格式缓存"""
        json_str = json.dumps(value, ensure_ascii=False)
        await self.set(key, json_str, ttl)


# 全局 Redis 管理器实例
redis_manager = RedisManager()