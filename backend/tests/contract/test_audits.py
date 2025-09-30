"""
Contract Test - Audit Endpoints
验证审核相关端点功能和响应格式

这个测试**必须失败**，因为端点尚未实现。
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app

# 创建测试客户端
client = TestClient(app)


@pytest.mark.parametrize(
    "audit_payload",
    [
        {
            "application_id": "123e4567-e89b-12d3-a456-426614174000",
            "action": "start_review",
            "result": "in_progress",
        },
        {
            "application_id": "123e4567-e89b-12d3-a456-426614174000",
            "action": "approve",
            "result": "approved",
            "comment": "审核通过",
        },
        {
            "application_id": "123e4567-e89b-12d3-a456-426614174000",
            "action": "reject",
            "result": "rejected",
            "comment": "资质不符合要求",
        },
        {
            "application_id": "123e4567-e89b-12d3-a456-426614174000",
            "action": "request_supplement",
            "result": "pending_supplement",
            "comment": "请补充营业执照副本",
        },
    ],
)
def test_create_audit_valid_payloads(audit_payload):
    """
    测试创建审核记录（有效载荷）

    预期结果：
    - 404 Not Found（端点未实现）
    """
    response = client.post("/api/v1/audits", json=audit_payload)

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


@pytest.mark.parametrize(
    "invalid_payload,expected_error_field",
    [
        (
            {
                # reject 时 comment 必填
                "application_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "reject",
                "result": "rejected",
                # 缺少 comment
            },
            "comment",
        ),
        (
            {
                # request_supplement 时 comment 必填
                "application_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "request_supplement",
                "result": "pending_supplement",
                # 缺少 comment
            },
            "comment",
        ),
        (
            {
                # 无效的 action
                "application_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "invalid_action",
                "result": "approved",
            },
            "action",
        ),
    ],
)
def test_create_audit_invalid_payloads(invalid_payload, expected_error_field):
    """
    测试无效审核载荷验证

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：400 Bad Request（验证失败）
    """
    response = client.post("/api/v1/audits", json=invalid_payload)

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


def test_get_audit_history():
    """
    测试查询审核历史

    预期结果：
    - 404 Not Found（端点未实现）
    """
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/api/v1/audits/history/{fake_uuid}")

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


def test_get_audit_history_invalid_uuid():
    """
    测试无效 UUID

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：422 Unprocessable Entity（UUID 格式错误）
    """
    invalid_uuid = "not-a-uuid"
    response = client.get(f"/api/v1/audits/history/{invalid_uuid}")

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])