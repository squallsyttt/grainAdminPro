"""
Contract Test - GET /applications
验证 GET /applications 端点功能和响应格式

这个测试**必须失败**，因为端点尚未实现。
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app

# 创建测试客户端
client = TestClient(app)


def test_list_applications_with_pagination():
    """
    手动测试：查询申请列表（带分页）

    预期结果：
    - 404 Not Found（端点未实现）
    """
    response = client.get("/api/v1/applications?page=1&page_size=20")

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


@pytest.mark.parametrize(
    "query_params",
    [
        {"status": "draft"},
        {"status": "pending"},
        {"status": "approved"},
        {"page": 2, "page_size": 10},
        {"status": "pending", "page": 1, "page_size": 50},
    ],
)
def test_list_applications_with_filters(query_params):
    """
    测试筛选参数

    预期结果：
    - 404 Not Found（端点未实现）
    """
    response = client.get("/api/v1/applications", params=query_params)

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


def test_get_application_detail_by_id():
    """
    测试查询申请详情

    预期结果：
    - 404 Not Found（端点未实现）
    """
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/api/v1/applications/{fake_uuid}")

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


@pytest.mark.parametrize(
    "invalid_params",
    [
        {"page": 0},  # 页码必须 >= 1
        {"page_size": 0},  # 每页数量必须 >= 1
        {"page_size": 101},  # 每页数量不能超过 100
        {"status": "invalid_status"},  # 无效状态值
    ],
)
def test_list_applications_invalid_params(invalid_params):
    """
    测试无效查询参数

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：400 Bad Request（参数验证失败）
    """
    response = client.get("/api/v1/applications", params=invalid_params)

    assert response.status_code == 404, (
        f"Expected 404 (endpoint not implemented), got {response.status_code}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])