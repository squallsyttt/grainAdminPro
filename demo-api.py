#!/usr/bin/env python3
"""
API 使用示例脚本
演示商家入驻管理系统的完整业务流程
"""
import asyncio
import httpx
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


class APIClient:
    """API 客户端封装"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None

    async def login(self, username: str, password: str) -> dict:
        """管理员登录"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password},
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                return data
            else:
                raise Exception(f"登录失败: {response.status_code} - {response.text}")

    async def get_headers(self) -> dict:
        """获取认证头"""
        if not self.token:
            raise Exception("请先登录")
        return {"Authorization": f"Bearer {self.token}"}

    async def create_application(self, data: dict) -> dict:
        """创建商家申请"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/applications",
                json=data,
                headers=await self.get_headers(),
            )
            return response.json()

    async def get_application(self, app_id: str) -> dict:
        """查询申请详情"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/applications/{app_id}",
                headers=await self.get_headers(),
            )
            return response.json()

    async def list_applications(self, status: Optional[str] = None) -> dict:
        """查询申请列表"""
        params = {}
        if status:
            params["status"] = status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/applications",
                params=params,
                headers=await self.get_headers(),
            )
            return response.json()

    async def submit_application(self, app_id: str) -> dict:
        """提交申请"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/applications/{app_id}/submit",
                headers=await self.get_headers(),
            )
            return response.json()

    async def start_audit(self, app_id: str) -> dict:
        """开始审核"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/audits",
                json={
                    "application_id": app_id,
                    "action": "start_review",
                    "result": "in_progress",
                    "comment": "开始审核申请",
                },
                headers=await self.get_headers(),
            )
            return response.json()

    async def approve_application(self, app_id: str, comment: str) -> dict:
        """审核通过"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/audits",
                json={
                    "application_id": app_id,
                    "action": "approve",
                    "result": "approved",
                    "comment": comment,
                },
                headers=await self.get_headers(),
            )
            return response.json()

    async def get_audit_history(self, app_id: str) -> dict:
        """查询审核历史"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/audits/history/{app_id}",
                headers=await self.get_headers(),
            )
            return response.json()


async def demo_workflow():
    """演示完整业务流程"""
    print("=" * 60)
    print("🎯 商家入驻管理系统 - 业务流程演示")
    print("=" * 60)
    print()

    client = APIClient()

    try:
        # 1. 管理员登录
        print("📝 步骤 1: 管理员登录")
        print("-" * 60)
        login_result = await client.login("admin", "admin123")
        print(f"✅ 登录成功！")
        print(f"   Access Token: {login_result['access_token'][:50]}...")
        print()

        # 2. 创建商家申请
        print("📝 步骤 2: 创建商家入驻申请")
        print("-" * 60)
        application_data = {
            "business_name": "示例科技有限公司",
            "unified_social_credit": "91110000000000000X",
            "legal_person_name": "张三",
            "legal_person_id_number": "110101199001011234",
            "contact_name": "李四",
            "contact_phone": "13800138000",
            "contact_email": "contact@example.com",
            "business_categories": ["电子产品", "软件服务"],
        }
        app = await client.create_application(application_data)
        app_id = app["id"]
        print(f"✅ 申请创建成功！")
        print(f"   申请 ID: {app_id}")
        print(f"   企业名称: {app['business_name']}")
        print(f"   当前状态: {app['status']}")
        print()

        # 3. 查询申请列表
        print("📝 步骤 3: 查询申请列表")
        print("-" * 60)
        app_list = await client.list_applications(status="draft")
        print(f"✅ 查询成功！")
        print(f"   草稿状态申请数量: {app_list['total']}")
        print()

        # 4. 提交申请
        print("📝 步骤 4: 提交申请")
        print("-" * 60)
        submitted_app = await client.submit_application(app_id)
        print(f"✅ 申请提交成功！")
        print(f"   当前状态: {submitted_app['status']}")
        print(f"   提交时间: {submitted_app.get('submitted_at', 'N/A')}")
        print()

        # 5. 开始审核
        print("📝 步骤 5: 开始审核")
        print("-" * 60)
        audit1 = await client.start_audit(app_id)
        print(f"✅ 审核已开始！")
        print(f"   审核记录 ID: {audit1['id']}")
        print(f"   审核动作: {audit1['action']}")
        print()

        # 6. 审核通过
        print("📝 步骤 6: 审核通过")
        print("-" * 60)
        audit2 = await client.approve_application(app_id, "审核通过，资质齐全")
        print(f"✅ 审核通过！")
        print(f"   审核结果: {audit2['result']}")
        print(f"   审核意见: {audit2['comment']}")
        print()

        # 7. 查询审核历史
        print("📝 步骤 7: 查询审核历史")
        print("-" * 60)
        history = await client.get_audit_history(app_id)
        print(f"✅ 审核历史查询成功！")
        print(f"   审核记录数量: {len(history.get('records', []))}")
        for i, record in enumerate(history.get("records", []), 1):
            print(f"   记录 {i}:")
            print(f"      动作: {record['action']}")
            print(f"      结果: {record['result']}")
            print(f"      审核员: {record['auditor_name']}")
        print()

        # 8. 查询最终状态
        print("📝 步骤 8: 查询最终申请状态")
        print("-" * 60)
        final_app = await client.get_application(app_id)
        print(f"✅ 查询成功！")
        print(f"   企业名称: {final_app['business_name']}")
        print(f"   最终状态: {final_app['status']}")
        print()

        print("=" * 60)
        print("🎉 业务流程演示完成！")
        print("=" * 60)

    except httpx.ConnectError:
        print("❌ 无法连接到 API 服务器")
        print("请确保 API 服务器正在运行:")
        print("   cd backend && uvicorn src.main:app --reload")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print()
    asyncio.run(demo_workflow())
    print()