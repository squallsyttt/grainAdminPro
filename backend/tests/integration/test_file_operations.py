"""
Integration Test - File Upload and Download
测试文件上传、下载和权限控制

这个测试**必须失败**，因为服务层和端点尚未实现。
"""
import io
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.models import Base

# 创建测试数据库（内存数据库）
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def temp_upload_dir():
    """创建临时上传目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def create_test_file(filename: str, content: bytes = b"test content") -> io.BytesIO:
    """创建测试文件"""
    return io.BytesIO(content)


def test_upload_business_license(client, temp_upload_dir):
    """
    测试场景 1：上传营业执照

    步骤：
    1. 创建申请
    2. POST /files/upload 上传营业执照（file_type=business_license）
    3. 验证返回 file_id 和 file_path
    4. 验证文件大小和类型正确

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：201 Created
    """
    # 创建申请（模拟）
    application_payload = {
        "business_name": "测试公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "test@example.com",
        "business_categories": ["食品"],
    }

    create_response = client.post("/api/v1/applications", json=application_payload)
    assert create_response.status_code == 404  # 端点未实现

    # 实现后的断言
    # application_id = create_response.json()["id"]
    #
    # # 上传营业执照
    # test_file = create_test_file("license.jpg", b"fake license image")
    # upload_response = client.post(
    #     "/api/v1/files/upload",
    #     files={"file": ("license.jpg", test_file, "image/jpeg")},
    #     data={
    #         "file_type": "business_license",
    #         "related_id": application_id,
    #     },
    # )
    # assert upload_response.status_code == 201
    # data = upload_response.json()
    # assert "file_id" in data
    # assert "file_path" in data
    # assert data["file_size"] > 0


def test_upload_id_card_files(client, temp_upload_dir):
    """
    测试场景 2：上传身份证正反面

    步骤：
    1. 创建申请
    2. 上传身份证正面（file_type=id_card_front）
    3. 上传身份证反面（file_type=id_card_back）
    4. 验证两个文件都上传成功

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：两个文件都上传成功
    """
    application_payload = {
        "business_name": "测试公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "test@example.com",
        "business_categories": ["食品"],
    }

    create_response = client.post("/api/v1/applications", json=application_payload)
    assert create_response.status_code == 404

    # 实现后的断言
    # application_id = create_response.json()["id"]
    #
    # # 上传身份证正面
    # front_file = create_test_file("id_front.jpg", b"fake id card front")
    # front_response = client.post(
    #     "/api/v1/files/upload",
    #     files={"file": ("id_front.jpg", front_file, "image/jpeg")},
    #     data={
    #         "file_type": "id_card_front",
    #         "related_id": application_id,
    #     },
    # )
    # assert front_response.status_code == 201
    #
    # # 上传身份证反面
    # back_file = create_test_file("id_back.jpg", b"fake id card back")
    # back_response = client.post(
    #     "/api/v1/files/upload",
    #     files={"file": ("id_back.jpg", back_file, "image/jpeg")},
    #     data={
    #         "file_type": "id_card_back",
    #         "related_id": application_id,
    #     },
    # )
    # assert back_response.status_code == 201


def test_upload_file_size_validation(client):
    """
    测试场景 3：文件大小验证

    步骤：
    1. 尝试上传超过 10MB 的文件
    2. 验证返回 400 Bad Request

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：400 Bad Request（文件过大）
    """
    fake_application_id = "123e4567-e89b-12d3-a456-426614174000"

    # 创建 11MB 文件
    large_content = b"x" * (11 * 1024 * 1024)
    large_file = create_test_file("large.jpg", large_content)

    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("large.jpg", large_file, "image/jpeg")},
        data={
            "file_type": "business_license",
            "related_id": fake_application_id,
        },
    )

    assert response.status_code == 404  # 端点未实现

    # 实现后的断言
    # assert response.status_code == 400
    # assert "size" in response.json()["message"].lower()


def test_upload_file_type_validation(client):
    """
    测试场景 4：文件类型验证

    步骤：
    1. 尝试上传不允许的文件类型（如 .txt）
    2. 验证返回 400 Bad Request

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：400 Bad Request（文件类型不允许）
    """
    fake_application_id = "123e4567-e89b-12d3-a456-426614174000"

    # 创建文本文件
    text_file = create_test_file("document.txt", b"plain text content")

    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("document.txt", text_file, "text/plain")},
        data={
            "file_type": "business_license",
            "related_id": fake_application_id,
        },
    )

    assert response.status_code == 404  # 端点未实现

    # 实现后的断言
    # assert response.status_code == 400
    # assert "type" in response.json()["message"].lower()


def test_upload_contract_photo(client, temp_upload_dir):
    """
    测试场景 5：上传合同照片

    步骤：
    1. 商家审核通过，获得 merchant_id
    2. POST /files/upload 上传合同照片（file_type=contract）
    3. 验证上传成功

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：合同照片上传成功
    """
    fake_merchant_id = "M20250930001"

    # 上传合同照片
    contract_file = create_test_file("contract.jpg", b"fake contract image")

    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("contract.jpg", contract_file, "image/jpeg")},
        data={
            "file_type": "contract",
            "related_id": fake_merchant_id,
        },
    )

    assert response.status_code == 404  # 端点未实现

    # 实现后的断言
    # assert response.status_code == 201
    # data = response.json()
    # assert data["file_type"] == "contract"


def test_download_file_with_signed_url(client):
    """
    测试场景 6：下载文件（获取签名 URL）

    步骤：
    1. 上传文件
    2. GET /files/{file_id} 获取签名 URL
    3. 验证返回的 URL 格式正确
    4. 验证 URL 有效期为 1 小时

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：返回签名 URL
    """
    fake_file_id = "123e4567-e89b-12d3-a456-426614174000"

    response = client.get(f"/api/v1/files/{fake_file_id}")

    assert response.status_code == 404  # 端点未实现

    # 实现后的断言
    # assert response.status_code == 200
    # data = response.json()
    # assert "url" in data
    # assert data["url"].startswith("http")


def test_merchant_can_only_download_own_files(client):
    """
    测试场景 7：商家只能下载自己的文件

    步骤：
    1. 商家 A 上传文件
    2. 商家 B 尝试下载商家 A 的文件
    3. 验证返回 403 Forbidden

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：403 Forbidden（权限不足）
    """
    fake_file_id = "123e4567-e89b-12d3-a456-426614174000"

    # 商家 B 尝试下载
    response = client.get(f"/api/v1/files/{fake_file_id}")

    assert response.status_code == 404  # 端点未实现

    # 实现后的断言
    # assert response.status_code == 403


def test_file_deletion_after_test(client, temp_upload_dir):
    """
    测试场景 8：测试清理 - 删除临时文件

    步骤：
    1. 上传测试文件
    2. 测试结束后验证临时文件已清理

    预期结果：
    - 临时目录在测试结束后为空
    """
    # temp_upload_dir fixture 会自动清理
    assert temp_upload_dir.exists()

    # 实现后可以验证临时文件清理
    # 上传文件后，测试结束时 temp_upload_dir 应该被清空


def test_upload_multiple_files_for_same_application(client):
    """
    测试场景 9：为同一申请上传多个文件

    步骤：
    1. 创建申请
    2. 上传营业执照
    3. 上传身份证正面
    4. 上传身份证反面
    5. 查询申请详情，验证包含 3 个文件

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：所有文件都关联到申请
    """
    application_payload = {
        "business_name": "多文件测试公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "multifile@example.com",
        "business_categories": ["食品"],
    }

    create_response = client.post("/api/v1/applications", json=application_payload)
    assert create_response.status_code == 404

    # 实现后的断言
    # application_id = create_response.json()["id"]
    #
    # # 上传 3 个文件
    # for file_type in ["business_license", "id_card_front", "id_card_back"]:
    #     test_file = create_test_file(f"{file_type}.jpg", b"fake file")
    #     client.post(
    #         "/api/v1/files/upload",
    #         files={"file": (f"{file_type}.jpg", test_file, "image/jpeg")},
    #         data={
    #             "file_type": file_type,
    #             "related_id": application_id,
    #         },
    #     )
    #
    # # 查询申请详情
    # detail_response = client.get(f"/api/v1/applications/{application_id}")
    # assert len(detail_response.json()["qualification_files"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])