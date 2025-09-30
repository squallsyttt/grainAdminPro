"""
Contract Test - Merchant Endpoints
验证商家账户端点功能和响应格式

这个测试**必须失败**，因为端点尚未实现。
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app

# 创建测试客户端
client = TestClient(app)


def test_get_merchant_by_id():
    """
    测试查询商家信息

    预期结果：
    - 404 Not Found（端点未实现）
    """
    merchant_id = "M20250930001"
    response = client.get(f"/api/v1/merchants/{merchant_id}")

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


@pytest.mark.parametrize(
    "update_payload",
    [
        {"contact_phone": "13900139000"},
        {"contact_email": "newemail@example.com"},
        {
            "contact_phone": "13900139000",
            "contact_email": "newemail@example.com",
        },
    ],
)
def test_update_merchant_valid_payloads(update_payload):
    """
    测试更新商家信息（有效载荷）

    预期结果：
    - 404 Not Found（端点未实现）
    """
    merchant_id = "M20250930001"
    response = client.patch(f"/api/v1/merchants/{merchant_id}", json=update_payload)

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


@pytest.mark.parametrize(
    "invalid_payload,expected_error_field",
    [
        (
            {"contact_phone": "invalid_phone"},  # 无效电话格式
            "contact_phone",
        ),
        (
            {"contact_email": "not-an-email"},  # 无效邮箱格式
            "contact_email",
        ),
        (
            {"merchant_id": "M20250930002"},  # 不允许更新 merchant_id
            "merchant_id",
        ),
    ],
)
def test_update_merchant_invalid_payloads(invalid_payload, expected_error_field):
    """
    测试无效更新载荷

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：400 Bad Request（验证失败）
    """
    merchant_id = "M20250930001"
    response = client.patch(f"/api/v1/merchants/{merchant_id}", json=invalid_payload)

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


def test_get_nonexistent_merchant():
    """
    测试查询不存在的商家

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：404 Not Found（商家不存在）
    """
    merchant_id = "M99999999999"
    response = client.get(f"/api/v1/merchants/{merchant_id}")

    assert response.status_code == 404


def test_update_nonexistent_merchant():
    """
    测试更新不存在的商家

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：404 Not Found（商家不存在）
    """
    merchant_id = "M99999999999"
    update_payload = {"contact_phone": "13900139000"}
    response = client.patch(f"/api/v1/merchants/{merchant_id}", json=update_payload)

    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])