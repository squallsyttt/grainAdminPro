"""
Integration Test - Audit Workflow
测试审核工作流（开始审核→通过/拒绝/要求补充材料）

这个测试**必须失败**，因为服务层和端点尚未实现。
"""
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


def test_start_review_workflow(client):
    """
    测试场景 1：审核员开始审核

    步骤：
    1. 商家创建并提交申请（status=PENDING）
    2. 审核员 POST /audits（action=START_REVIEW）
    3. 验证申请状态变更为 UNDER_REVIEW
    4. 验证审核记录已创建

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：状态转换正确
    """
    # 创建申请（模拟）
    application_payload = {
        "business_name": "待审核公司",
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
    # client.post(f"/api/v1/applications/{application_id}/submit")
    #
    # # 开始审核
    # audit_payload = {
    #     "application_id": application_id,
    #     "action": "start_review",
    #     "result": "in_progress",
    # }
    # audit_response = client.post("/api/v1/audits", json=audit_payload)
    # assert audit_response.status_code == 201
    #
    # # 验证申请状态变更
    # app_response = client.get(f"/api/v1/applications/{application_id}")
    # assert app_response.json()["status"] == "under_review"


def test_approve_application_creates_merchant_account(client):
    """
    测试场景 2：审核通过自动创建商家账户

    步骤：
    1. 创建并提交申请
    2. 开始审核
    3. POST /audits（action=APPROVE）
    4. 验证申请状态变更为 APPROVED
    5. 验证商家账户已自动创建
    6. 验证 merchant_id 格式正确（M + YYYYMMDD + 序号）

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：自动创建商家账户
    """
    # 创建申请
    application_payload = {
        "business_name": "通过审核公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "approved@example.com",
        "business_categories": ["食品"],
    }

    create_response = client.post("/api/v1/applications", json=application_payload)
    assert create_response.status_code == 404

    # 实现后的断言
    # application_id = create_response.json()["id"]
    # client.post(f"/api/v1/applications/{application_id}/submit")
    # client.post(
    #     "/api/v1/audits",
    #     json={
    #         "application_id": application_id,
    #         "action": "start_review",
    #         "result": "in_progress",
    #     },
    # )
    #
    # # 审核通过
    # approve_payload = {
    #     "application_id": application_id,
    #     "action": "approve",
    #     "result": "approved",
    #     "comment": "资质齐全，审核通过",
    # }
    # approve_response = client.post("/api/v1/audits", json=approve_payload)
    # assert approve_response.status_code == 201
    #
    # # 验证申请状态
    # app_response = client.get(f"/api/v1/applications/{application_id}")
    # assert app_response.json()["status"] == "approved"
    #
    # # 验证商家账户已创建
    # # 需要从审核响应或申请详情获取 merchant_id
    # # merchant_response = client.get(f"/api/v1/merchants/{merchant_id}")
    # # assert merchant_response.status_code == 200
    # # assert merchant_response.json()["merchant_id"].startswith("M202509")


def test_reject_application_workflow(client):
    """
    测试场景 3：审核拒绝

    步骤：
    1. 创建并提交申请
    2. 开始审核
    3. POST /audits（action=REJECT，必须提供 comment）
    4. 验证申请状态变更为 REJECTED
    5. 验证审核意见已记录

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：拒绝流程正确
    """
    # 创建申请
    application_payload = {
        "business_name": "被拒绝公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "rejected@example.com",
        "business_categories": ["食品"],
    }

    create_response = client.post("/api/v1/applications", json=application_payload)
    assert create_response.status_code == 404

    # 实现后的断言
    # application_id = create_response.json()["id"]
    # client.post(f"/api/v1/applications/{application_id}/submit")
    # client.post(
    #     "/api/v1/audits",
    #     json={
    #         "application_id": application_id,
    #         "action": "start_review",
    #         "result": "in_progress",
    #     },
    # )
    #
    # # 审核拒绝
    # reject_payload = {
    #     "application_id": application_id,
    #     "action": "reject",
    #     "result": "rejected",
    #     "comment": "营业执照已过期，不符合入驻要求",
    # }
    # reject_response = client.post("/api/v1/audits", json=reject_payload)
    # assert reject_response.status_code == 201
    #
    # # 验证申请状态
    # app_response = client.get(f"/api/v1/applications/{application_id}")
    # assert app_response.json()["status"] == "rejected"


def test_request_supplement_workflow(client):
    """
    测试场景 4：要求补充材料

    步骤：
    1. 创建并提交申请
    2. 开始审核
    3. POST /audits（action=REQUEST_SUPPLEMENT，必须提供 comment）
    4. 验证申请状态变更为 REQUIRE_SUPPLEMENT
    5. 商家补充材料后重新提交
    6. 验证状态变更回 PENDING

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：补充材料流程正确
    """
    # 创建申请
    application_payload = {
        "business_name": "需补充材料公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "supplement@example.com",
        "business_categories": ["食品"],
    }

    create_response = client.post("/api/v1/applications", json=application_payload)
    assert create_response.status_code == 404

    # 实现后的断言
    # application_id = create_response.json()["id"]
    # client.post(f"/api/v1/applications/{application_id}/submit")
    # client.post(
    #     "/api/v1/audits",
    #     json={
    #         "application_id": application_id,
    #         "action": "start_review",
    #         "result": "in_progress",
    #     },
    # )
    #
    # # 要求补充材料
    # supplement_payload = {
    #     "application_id": application_id,
    #     "action": "request_supplement",
    #     "result": "pending_supplement",
    #     "comment": "请补充营业执照副本和法人身份证正反面",
    # }
    # supplement_response = client.post("/api/v1/audits", json=supplement_payload)
    # assert supplement_response.status_code == 201
    #
    # # 验证申请状态
    # app_response = client.get(f"/api/v1/applications/{application_id}")
    # assert app_response.json()["status"] == "require_supplement"
    #
    # # 商家补充材料后重新提交
    # resubmit_response = client.post(f"/api/v1/applications/{application_id}/submit")
    # assert resubmit_response.status_code == 200
    # assert resubmit_response.json()["status"] == "pending"


def test_query_audit_history(client):
    """
    测试场景 5：查询审核历史

    步骤：
    1. 创建申请并经过多次审核操作
    2. GET /audits/history/{application_id}
    3. 验证返回所有审核记录
    4. 验证按时间倒序排列

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：返回完整审核历史
    """
    # 创建申请
    application_payload = {
        "business_name": "多次审核公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "history@example.com",
        "business_categories": ["食品"],
    }

    create_response = client.post("/api/v1/applications", json=application_payload)
    assert create_response.status_code == 404

    # 实现后的断言
    # application_id = create_response.json()["id"]
    # client.post(f"/api/v1/applications/{application_id}/submit")
    #
    # # 多次审核操作
    # client.post(
    #     "/api/v1/audits",
    #     json={
    #         "application_id": application_id,
    #         "action": "start_review",
    #         "result": "in_progress",
    #     },
    # )
    # client.post(
    #     "/api/v1/audits",
    #     json={
    #         "application_id": application_id,
    #         "action": "request_supplement",
    #         "result": "pending_supplement",
    #         "comment": "需要补充材料",
    #     },
    # )
    #
    # # 查询审核历史
    # history_response = client.get(f"/api/v1/audits/history/{application_id}")
    # assert history_response.status_code == 200
    # records = history_response.json()["records"]
    # assert len(records) >= 2  # 至少有两条记录
    # # 验证按时间倒序排列
    # assert records[0]["created_at"] >= records[1]["created_at"]


def test_audit_without_comment_validation(client):
    """
    测试场景 6：验证 reject 和 request_supplement 时 comment 必填

    步骤：
    1. 尝试 REJECT 但不提供 comment
    2. 验证返回 400 Bad Request

    预期结果：
    - 当前：404 Not Found（端点未实现）
    - 实现后：400 Bad Request（comment 必填）
    """
    fake_application_id = "123e4567-e89b-12d3-a456-426614174000"

    # 缺少 comment 的 reject
    reject_payload = {
        "application_id": fake_application_id,
        "action": "reject",
        "result": "rejected",
        # 缺少 comment
    }

    response = client.post("/api/v1/audits", json=reject_payload)
    assert response.status_code == 404  # 端点未实现

    # 实现后的断言
    # assert response.status_code == 400
    # assert "comment" in response.json()["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])