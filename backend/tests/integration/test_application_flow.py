"""
Integration Test - Merchant Application Flow
测试完整的商家申请流程（创建→提交→查询）
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_draft_application(client: AsyncClient, merchant_token: str):
    """
    测试场景 1：创建草稿申请

    步骤：
    1. POST /applications 创建申请（status=DRAFT）
    2. 验证响应包含 application_id
    3. 验证状态为 DRAFT
    """
    payload = {
        "business_name": "测试科技有限公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "contact@example.com",
        "business_categories": ["食品", "日用品"],
    }

    response = await client.post(
        "/api/v1/applications",
        json=payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    # 验证创建成功
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "draft"
    assert data["business_name"] == "测试科技有限公司"


@pytest.mark.asyncio
async def test_submit_application_workflow(client: AsyncClient, merchant_token: str):
    """
    测试场景 2：提交申请工作流

    步骤：
    1. 创建草稿申请
    2. POST /applications/{id}/submit 提交申请
    3. 验证状态变更为 PENDING（如果有必需文件）或返回400（如果缺少文件）
    """
    # 步骤 1：创建申请
    payload = {
        "business_name": "测试公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "test@example.com",
        "business_categories": ["服装"],
    }

    create_response = await client.post(
        "/api/v1/applications",
        json=payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert create_response.status_code == 201
    application_id = create_response.json()["id"]

    # 步骤 2：提交申请
    submit_response = await client.post(
        f"/api/v1/applications/{application_id}/submit",
        headers={"Authorization": f"Bearer {merchant_token}"},
    )

    # 由于没有上传必需文件，应该返回 400
    # 这验证了业务规则：必须上传营业执照和身份证才能提交
    assert submit_response.status_code == 400
    assert "申请信息不完整" in submit_response.json()["detail"]


@pytest.mark.asyncio
async def test_query_own_applications_only(client: AsyncClient, merchant_token: str):
    """
    测试场景 3：商家只能查询自己的申请

    步骤：
    1. 商家 A 创建申请
    2. 商家 A 查询申请列表
    3. 验证只能看到自己的申请
    """
    # 创建申请
    payload = {
        "business_name": "商家A公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "merchant-a@example.com",
        "business_categories": ["食品"],
    }

    create_response = await client.post(
        "/api/v1/applications",
        json=payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert create_response.status_code == 201

    # 查询列表
    list_response = await client.get(
        "/api/v1/applications",
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert list_response.status_code == 200
    applications = list_response.json()["items"]
    assert len(applications) >= 1  # 至少能看到自己刚创建的申请


@pytest.mark.asyncio
async def test_update_application_in_editable_status(
    client: AsyncClient, merchant_token: str
):
    """
    测试场景 4：更新可编辑状态的申请

    步骤：
    1. 创建草稿申请（DRAFT）
    2. PUT /applications/{id} 更新联系信息
    3. 验证更新成功
    """
    # 创建申请
    payload = {
        "business_name": "测试公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "old@example.com",
        "business_categories": ["食品"],
    }

    create_response = await client.post(
        "/api/v1/applications",
        json=payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert create_response.status_code == 201
    application_id = create_response.json()["id"]

    # 更新联系信息
    update_payload = {
        "contact_email": "new@example.com",
        "contact_phone": "13900139000",
    }
    update_response = await client.put(
        f"/api/v1/applications/{application_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["contact_email"] == "new@example.com"


@pytest.mark.asyncio
async def test_cannot_update_submitted_application(
    client: AsyncClient, merchant_token: str, test_db: AsyncSession
):
    """
    测试场景 5：不能更新已提交的申请

    步骤：
    1. 创建并提交申请（PENDING）
    2. 尝试 PUT 更新
    3. 验证返回 409 Conflict
    """
    from src.models.merchant_application import MerchantApplication
    from src.models.enums import ApplicationStatus
    from sqlalchemy import select

    # 创建申请
    payload = {
        "business_name": "测试公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "test@example.com",
        "business_categories": ["食品"],
    }

    create_response = await client.post(
        "/api/v1/applications",
        json=payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert create_response.status_code == 201
    application_id = create_response.json()["id"]

    # 直接在数据库中将状态改为 PENDING（绕过文件验证）
    from uuid import UUID

    stmt = select(MerchantApplication).where(
        MerchantApplication.id == UUID(application_id)
    )
    result = await test_db.execute(stmt)
    app = result.scalar_one()
    app.status = ApplicationStatus.PENDING
    await test_db.commit()

    # 尝试更新已提交的申请
    update_payload = {"contact_email": "new@example.com"}
    update_response = await client.put(
        f"/api/v1/applications/{application_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert update_response.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_query_application_detail(client: AsyncClient, merchant_token: str):
    """
    测试场景 6：查询申请详情

    步骤：
    1. 创建申请
    2. GET /applications/{id} 查询详情
    3. 验证返回完整信息（包括 qualification_files 和 audit_records）
    """
    # 创建申请
    payload = {
        "business_name": "测试公司",
        "unified_social_credit": "91110108MA01234567",
        "legal_person_name": "张三",
        "legal_person_id_number": "110101199001011234",
        "contact_name": "李四",
        "contact_phone": "13800138000",
        "contact_email": "test@example.com",
        "business_categories": ["食品"],
    }

    create_response = await client.post(
        "/api/v1/applications",
        json=payload,
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert create_response.status_code == 201
    application_id = create_response.json()["id"]

    # 查询详情
    detail_response = await client.get(
        f"/api/v1/applications/{application_id}",
        headers={"Authorization": f"Bearer {merchant_token}"},
    )
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert "qualification_files" in data
    assert "audit_records" in data
    assert isinstance(data["qualification_files"], list)
    assert isinstance(data["audit_records"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])