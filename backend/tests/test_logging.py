"""
测试结构化日志和 Correlation ID 功能
"""
import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_correlation_id_in_response():
    """测试响应中包含 Correlation ID"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    assert len(response.headers["X-Correlation-ID"]) == 36  # UUID 长度


@pytest.mark.asyncio
async def test_custom_correlation_id():
    """测试自定义 Correlation ID 会被保留"""
    custom_cid = "my-custom-correlation-id-123"

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={"X-Correlation-ID": custom_cid}
        )

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == custom_cid


@pytest.mark.asyncio
async def test_health_endpoint():
    """测试健康检查端点"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "env" in data
    assert "version" in data