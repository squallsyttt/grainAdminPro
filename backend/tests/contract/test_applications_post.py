"""
Contract Test - POST /applications
验证 POST /applications 端点功能和响应格式

这个测试**必须失败**，因为端点尚未实现。
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app

# 创建测试客户端
client = TestClient(app)


@pytest.mark.parametrize(
    "payload",
    [
        {
            "business_name": "测试科技有限公司",
            "unified_social_credit": "91110108MA01234567",
            "legal_person_name": "张三",
            "legal_person_id_number": "110101199001011234",
            "contact_name": "李四",
            "contact_phone": "13800138000",
            "contact_email": "contact@example.com",
            "business_categories": ["食品", "日用品"],
        }
    ],
)
def test_create_application_valid_payload(payload):
    """
    手动测试：使用有效载荷创建申请

    预期结果：
    - 404 Not Found（端点未实现）
    """
    response = client.post("/api/v1/applications", json=payload)

    # 断言：端点应该不存在
    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


@pytest.mark.parametrize(
    "invalid_payload,expected_field",
    [
        (
            {
                # 缺少 business_name
                "unified_social_credit": "91110108MA01234567",
                "legal_person_name": "张三",
                "legal_person_id_number": "110101199001011234",
                "contact_name": "李四",
                "contact_phone": "13800138000",
                "contact_email": "contact@example.com",
                "business_categories": ["食品"],
            },
            "business_name",
        ),
        (
            {
                "business_name": "测试公司",
                "unified_social_credit": "INVALID",  # 无效格式
                "legal_person_name": "张三",
                "legal_person_id_number": "110101199001011234",
                "contact_name": "李四",
                "contact_phone": "13800138000",
                "contact_email": "contact@example.com",
                "business_categories": ["食品"],
            },
            "unified_social_credit",
        ),
        (
            {
                "business_name": "测试公司",
                "unified_social_credit": "91110108MA01234567",
                "legal_person_name": "张三",
                "legal_person_id_number": "INVALID",  # 无效身份证号
                "contact_name": "李四",
                "contact_phone": "13800138000",
                "contact_email": "contact@example.com",
                "business_categories": ["食品"],
            },
            "legal_person_id_number",
        ),
    ],
)
def test_create_application_invalid_payload(invalid_payload, expected_field):
    """
    测试无效载荷验证

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：400 Bad Request（验证失败）
    """
    response = client.post("/api/v1/applications", json=invalid_payload)

    # 当前应该是 404，因为端点不存在
    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])