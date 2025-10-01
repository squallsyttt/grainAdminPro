#!/usr/bin/env python
"""
Quickstart 验证脚本
验证商家入驻管理系统的核心功能
"""
import sys
import json
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app
from src.core.database import get_db, engine
from src.models.base import Base
from sqlalchemy.orm import Session
import asyncio

# 测试数据
TEST_APPLICATION = {
    "business_name": "测试科技有限公司",
    "unified_social_credit": "91110000MA01234567",
    "legal_person_name": "张三",
    "legal_person_id_number": "110101199001011234",
    "contact_name": "李四",
    "contact_phone": "13800138000",
    "contact_email": "test@example.com",
    "business_categories": ["食品饮料", "数码家电"]
}

def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_success(message: str):
    """打印成功消息"""
    print(f"✅ {message}")

def print_error(message: str):
    """打印错误消息"""
    print(f"❌ {message}")

def print_info(message: str):
    """打印信息"""
    print(f"ℹ️  {message}")

def verify_database_connection():
    """验证数据库连接"""
    print_section("验证数据库连接")

    try:
        db = next(get_db())
        result = db.execute("SELECT 1").scalar()
        if result == 1:
            print_success("数据库连接成功")
            return True
        else:
            print_error("数据库连接失败")
            return False
    except Exception as e:
        print_error(f"数据库连接失败: {str(e)}")
        return False

def verify_tables_exist():
    """验证数据表是否存在"""
    print_section("验证数据表结构")

    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = [
            'merchant_application',
            'audit_record',
            'merchant_account',
            'contract_file',
            'qualification_file'
        ]

        for table in required_tables:
            if table in tables:
                print_success(f"表 {table} 存在")
            else:
                print_error(f"表 {table} 不存在")
                return False

        return True
    except Exception as e:
        print_error(f"检查表结构失败: {str(e)}")
        return False

def verify_models_can_import():
    """验证模型可以导入"""
    print_section("验证模型导入")

    try:
        from src.models.merchant_application import MerchantApplication
        from src.models.audit_record import AuditRecord
        from src.models.merchant_account import MerchantAccount
        from src.models.contract_file import ContractFile
        from src.models.qualification_file import QualificationFile

        print_success("所有模型导入成功")
        return True
    except Exception as e:
        print_error(f"模型导入失败: {str(e)}")
        return False

def verify_schemas_can_import():
    """验证 Schemas 可以导入"""
    print_section("验证 Schemas 导入")

    try:
        from src.schemas.application import CreateApplicationRequest, ApplicationResponse
        from src.schemas.audit import CreateAuditRequest, AuditResponse
        from src.schemas.merchant import MerchantResponse

        print_success("所有 Schemas 导入成功")
        return True
    except Exception as e:
        print_error(f"Schemas 导入失败: {str(e)}")
        return False

def verify_services_can_import():
    """验证服务层可以导入"""
    print_section("验证服务层导入")

    try:
        from src.services.application_service import ApplicationService
        from src.services.audit_service import AuditService
        from src.services.merchant_service import MerchantService

        print_success("所有服务层导入成功")
        return True
    except Exception as e:
        print_error(f"服务层导入失败: {str(e)}")
        return False

def verify_api_endpoints():
    """验证 API 端点"""
    print_section("验证 API 端点")

    try:
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append((route.path, list(route.methods)))

        print_info(f"找到 {len(routes)} 个路由")

        # 检查关键端点
        key_endpoints = [
            ('/health', 'GET'),
            ('/api/v1/applications', 'GET'),
            ('/api/v1/applications', 'POST'),
            ('/api/v1/audits', 'POST'),
        ]

        for path, method in key_endpoints:
            found = any(route_path == path and method in methods
                       for route_path, methods in routes)
            if found:
                print_success(f"端点 {method} {path} 已注册")
            else:
                print_error(f"端点 {method} {path} 未找到")

        return True
    except Exception as e:
        print_error(f"验证端点失败: {str(e)}")
        return False

def verify_redis_connection():
    """验证 Redis 连接"""
    print_section("验证 Redis 连接")

    try:
        from src.core.cache import cache_manager

        # 测试 Redis 连接
        test_key = "quickstart_test"
        test_value = "test_value"

        cache_manager.set(test_key, test_value, expire=10)
        retrieved_value = cache_manager.get(test_key)

        if retrieved_value == test_value:
            print_success("Redis 连接成功，读写正常")
            cache_manager.delete(test_key)
            return True
        else:
            print_error("Redis 读写失败")
            return False
    except Exception as e:
        print_error(f"Redis 连接失败: {str(e)}")
        return False

def main():
    """主验证流程"""
    print("\n" + "="*60)
    print("  商家入驻管理系统 - Quickstart 验证")
    print("="*60)
    print(f"  时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    results = []

    # 执行各项验证
    results.append(("数据库连接", verify_database_connection()))
    results.append(("数据表结构", verify_tables_exist()))
    results.append(("模型导入", verify_models_can_import()))
    results.append(("Schemas导入", verify_schemas_can_import()))
    results.append(("服务层导入", verify_services_can_import()))
    results.append(("API端点", verify_api_endpoints()))
    results.append(("Redis连接", verify_redis_connection()))

    # 汇总结果
    print_section("验证结果汇总")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name:<20} {status}")

    print(f"\n总计: {passed}/{total} 项验证通过")

    if passed == total:
        print_success("所有验证项通过！系统功能正常 🎉")
        return 0
    else:
        print_error(f"有 {total - passed} 项验证失败，请检查日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())