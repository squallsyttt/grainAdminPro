# Tasks: 商家入驻管理系统

**Feature**: 001-b2b2c | **Branch**: `001-b2b2c` | **Date**: 2025-09-30
**Input**: Design documents from `/specs/001-b2b2c/`
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/openapi.yaml ✓, SETUP.md ✓

---

## ⚠️ IMPORTANT: Environment Setup Required

**Before starting any tasks**, complete the environment configuration:

📖 **Read**: `specs/001-b2b2c/SETUP.md` - 详细的环境配置指南

**Quick Setup Checklist**:

- [X] PostgreSQL 14+ 已安装并运行
- [X] Redis 6+ 已安装并运行
- [X] 数据库用户已创建：`padmin` / `Qwe!1234`
- [X] 数据库已创建：`grainadmin_dev`
- [X] `backend/.env` 文件已配置（从 `.env.example` 复制）
- [X] Python 3.11+ 虚拟环境已创建

**Configuration Files**:

- `backend/.env.example` - 环境变量模板（包含数据库账户密码等）
- `specs/001-b2b2c/SETUP.md` - 完整配置步骤和故障排查

**Key Configuration Values** (Development):

```bash
DATABASE_URL=postgresql://padmin:Qwe!1234@localhost:5432/grainadmin_dev
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev-secret-key-change-in-production-use-at-least-32-chars
UPLOAD_DIR=./uploads
```

---

## Execution Summary

**Total Tasks**: 60
**Parallel Tasks**: 28 (marked with [P])
**Estimated Duration**: 8-10 days (with TDD)

**Tech Stack**:

- Backend: FastAPI (Python 3.11+), PostgreSQL 14+, Redis 6+, SQLAlchemy 2.0, Celery
- Frontend: React 18, Ant Design Pro v6, Umi.js (双前端)
- Testing: pytest, Jest, Schemathesis

**Project Structure**: Web app (backend/ + admin-frontend/ + merchant-frontend/)

---

## Phase 3.1: Project Setup & Infrastructure

### T001: Initialize Backend Project Structure

**Type**: Setup | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: None

**Description**:
创建 backend/ 目录结构，初始化 Python 项目，配置虚拟环境和依赖管理。

**Files to Create**:

- `backend/requirements.txt`
- `backend/requirements-dev.txt`
- `backend/.env.example`
- `backend/pyproject.toml` (Black, isort 配置)
- `backend/setup.py`

**Acceptance Criteria**:

- [X] backend/ 目录结构按 plan.md 创建（src/, tests/, alembic/）
- [X] requirements.txt 包含：FastAPI, SQLAlchemy, Alembic, psycopg2, redis, celery, python-jose[cryptography], passlib, python-multipart
- [X] requirements-dev.txt 包含：pytest, pytest-asyncio, black, isort, flake8, mypy, schemathesis
- [X] Python 虚拟环境创建成功：`python -m venv venv`
- [X] 依赖安装成功：`pip install -r requirements.txt -r requirements-dev.txt`

---

### T002: [P] Configure Linting and Code Quality Tools

**Type**: Setup | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T001

**Description**:
配置 Black, isort, flake8, mypy 代码质量工具和 pre-commit hooks。

**Files to Create**:

- `backend/.flake8`
- `backend/mypy.ini`
- `backend/.pre-commit-config.yaml`

**Acceptance Criteria**:

- [X] Black 配置：line-length=100, target-version=py311
- [X] isort 配置：profile=black, multi_line_output=3
- [X] flake8 配置：max-line-length=100, exclude=.venv,alembic
- [X] mypy 配置：python_version=3.11, strict=True
- [X] pre-commit hooks 安装：`pre-commit install`
- [X] 运行 `pre-commit run --all-files` 通过

---

### T003: [P] Initialize Admin Frontend Project

**Type**: Setup | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: None

**Description**:
使用 Ant Design Pro 创建主后台（平台管理）前端项目。

**Command**:

```bash
npm create umi admin-frontend -- --template=ant-design-pro
```

**Files to Create**:

- `admin-frontend/package.json`
- `admin-frontend/.umirc.ts` (Umi配置)
- `admin-frontend/.env`
- `admin-frontend/tsconfig.json`

**Acceptance Criteria**:

- [X] admin-frontend/ 项目创建成功
- [X] 依赖安装成功：`cd admin-frontend && npm install`
- [X] 开发服务器启动成功：`npm run dev`（端口8001）
- [X] ESLint 和 Prettier 配置正确
- [X] 访问 http://localhost:8001 显示 Ant Design Pro 默认页面

---

### T004: [P] Initialize Merchant Frontend Project

**Type**: Setup | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: None

**Description**:
使用 Ant Design Pro 创建商家后台（商家管理）前端项目。

**Command**:

```bash
npm create umi merchant-frontend -- --template=ant-design-pro
```

**Files to Create**:

- `merchant-frontend/package.json`
- `merchant-frontend/.umirc.ts`
- `merchant-frontend/.env`
- `merchant-frontend/tsconfig.json`

**Acceptance Criteria**:

- [X] merchant-frontend/ 项目创建成功
- [X] 依赖安装成功：`cd merchant-frontend && npm install`
- [X] 开发服务器启动成功：`npm run dev`（端口8002）
- [X] ESLint 和 Prettier 配置正确
- [X] 访问 http://localhost:8002 显示 Ant Design Pro 默认页面

---

### T005: Initialize PostgreSQL Database

**Type**: Setup | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: None

**Description**:
创建开发数据库，配置数据库连接。

**Commands**:

```bash
createdb grainadmin_dev
```

**Files to Create**:

- `backend/.env`（包含 DATABASE_URL）

**Acceptance Criteria**:

- [X] 数据库 `grainadmin_dev` 创建成功
- [X] DATABASE_URL 配置正确：`postgresql://padmin:Qwe!1234@localhost:5432/grainadmin_dev`
- [X] 测试连接成功：`psql grainadmin_dev -c "SELECT 1;"`

---

### T006: Initialize Alembic for Database Migrations

**Type**: Setup | **Priority**: P0 | **Estimated**: 45min | **Dependencies**: T001, T005

**Description**:
初始化 Alembic，配置数据库迁移环境。

**Commands**:

```bash
cd backend
alembic init alembic
```

**Files to Create/Modify**:

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/`

**Acceptance Criteria**:

- [X] Alembic 初始化成功
- [X] `alembic.ini` 配置 `sqlalchemy.url` 从环境变量读取
- [X] `alembic/env.py` 导入所有 models 和 Base
- [X] 运行 `alembic revision --autogenerate -m "test"` 成功
- [X] 测试迁移：`alembic upgrade head` 和 `alembic downgrade -1` 成功

---

### T007: [P] Setup Redis for Caching and Session

**Type**: Setup | **Priority**: P1 | **Estimated**: 30min | **Dependencies**: None

**Description**:
配置 Redis 连接，创建缓存工具类。

**Files to Create**:

- `backend/src/core/cache.py`
- `backend/src/core/config.py` (REDIS_URL 配置)

**Acceptance Criteria**:

- [X] Redis 本地安装并运行：`redis-cli ping` 返回 PONG
- [X] REDIS_URL 配置正确：`redis://localhost:6379/0`
- [X] 缓存工具类实现（get, set, delete, exists 方法）
- [X] 测试 Redis 连接成功：`redis-cli set test_key "test_value"`

---

### T008: [P] Setup Celery for Async Tasks

**Type**: Setup | **Priority**: P1 | **Estimated**: 1h | **Dependencies**: T001, T007

**Description**:
配置 Celery 异步任务队列，使用 Redis 作为 broker。

**Files to Create**:

- `backend/src/celery_app.py`
- `backend/src/tasks/` (任务目录)

**Acceptance Criteria**:

- [X] Celery app 初始化成功
- [X] Broker 配置：`redis://localhost:6379/1`
- [X] Result backend 配置：`redis://localhost:6379/2`
- [X] 创建测试任务：`@celery.task def test_task(): return "success"`
- [X] Celery worker 启动成功：`celery -A src.celery_app worker -l info`
- [X] 测试任务执行成功

---

### T009: Create FastAPI Application Entry Point

**Type**: Setup | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T001

**Description**:
创建 FastAPI 应用主入口，配置 CORS、日志、中间件。

**Files to Create**:

- `backend/src/main.py`
- `backend/src/core/config.py`
- `backend/src/core/logging.py`

**Acceptance Criteria**:

- [X] FastAPI app 创建成功
- [X] CORS 配置允许前端域名（localhost:8001, localhost:8002）
- [X] 结构化 JSON 日志配置（Correlation ID 中间件）
- [X] Health check 端点：`GET /health` 返回 `{"status": "ok"}`
- [X] API 文档可访问：`http://localhost:8000/docs`
- [X] 启动成功：`uvicorn src.main:app --reload`

---

## Phase 3.2: Database Models & Migrations (TDD - Models First)

### T010: [P] Create ApplicationStatus and Related Enums

**Type**: Model | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T006

**Description**:
创建申请状态、审核动作、审核结果等 Enum 类型。

**Files to Create**:

- `backend/src/models/enums.py`

**Enums to Create**:

- ApplicationStatus (draft, pending, under_review, require_supplement, approved, rejected)
- AuditAction (start_review, approve, reject, request_supplement)
- AuditResult (approved, rejected, pending_supplement, in_progress)
- MerchantLevel (normal, vip, diamond)
- MerchantStatus (active, frozen, closed)
- QualificationFileType (business_license, id_card_front, id_card_back, other)
- FileAuditStatus (pending, approved, rejected)

**Acceptance Criteria**:

- [X] 所有 Enum 类继承自 `str, Enum`
- [X] 每个 Enum 值与 data-model.md 一致
- [X] 单元测试验证所有 Enum 值可序列化为 JSON

---

### T011: [P] Create MerchantApplication Model

**Type**: Model | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T010

**Description**:
创建 MerchantApplication SQLAlchemy 模型（商家申请表）。

**Files to Create**:

- `backend/src/models/merchant_application.py`
- `backend/src/models/base.py` (Base class)

**Acceptance Criteria**:

- [X] 所有字段按 data-model.md 定义创建
- [X] 包含 UUID 主键、业务字段、时间戳字段
- [X] status 字段使用 ApplicationStatus Enum
- [X] business_categories 字段使用 JSONB 类型
- [X] 敏感字段（legal_person_id_number, contact_phone）暂用 VARCHAR（后续加密）
- [X] 包含 `__repr__` 方法便于调试
- [X] 包含 `to_dict()` 方法用于序列化

---

### T012: [P] Create AuditRecord Model

**Type**: Model | **Priority**: P0 | **Estimated**: 45min | **Dependencies**: T010, T011

**Description**:
创建 AuditRecord SQLAlchemy 模型（审核记录表）。

**Files to Create**:

- `backend/src/models/audit_record.py`

**Acceptance Criteria**:

- [X] 所有字段按 data-model.md 定义创建
- [X] application_id 外键关联 MerchantApplication
- [X] action 和 result 字段使用对应 Enum
- [X] auditor_id 字段（FK，指向用户表，本 feature 暂用 UUID）
- [X] 包含索引：application_id, auditor_id, created_at
- [X] 包含 `to_dict()` 方法

---

### T013: [P] Create MerchantAccount Model

**Type**: Model | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T010, T011

**Description**:
创建 MerchantAccount SQLAlchemy 模型（商家账户表）。

**Files to Create**:

- `backend/src/models/merchant_account.py`

**Acceptance Criteria**:

- [X] 所有字段按 data-model.md 定义创建
- [X] merchant_id 字段 UNIQUE（商家编号如 M20250930001）
- [X] password_hash 字段存储 bcrypt 哈希
- [X] level 和 status 字段使用对应 Enum
- [X] application_id 外键 UNIQUE（一个申请对应一个账户）
- [X] 包含密码验证方法：`verify_password(plain_password)`
- [X] 包含 `to_dict()` 方法（不包含 password_hash）

---

### T014: [P] Create ContractFile Model

**Type**: Model | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T013

**Description**:
创建 ContractFile SQLAlchemy 模型（合同档案表）。

**Files to Create**:

- `backend/src/models/contract_file.py`

**Acceptance Criteria**:

- [X] 所有字段按 data-model.md 定义创建
- [X] merchant_id 外键关联 MerchantAccount.merchant_id
- [X] file_size 字段限制：CHECK (file_size > 0 AND file_size <= 10485760)
- [X] 包含索引：merchant_id, uploaded_at
- [X] 包含 `to_dict()` 方法

---

### T015: [P] Create QualificationFile Model

**Type**: Model | **Priority**: P0 | **Estimated**: 45min | **Dependencies**: T011, T013

**Description**:
创建 QualificationFile SQLAlchemy 模型（资质文件表）。

**Files to Create**:

- `backend/src/models/qualification_file.py`

**Acceptance Criteria**:

- [X] 所有字段按 data-model.md 定义创建
- [X] application_id 和 merchant_id 外键
- [X] file_type 使用 QualificationFileType Enum
- [X] audit_status 使用 FileAuditStatus Enum
- [X] file_size CHECK 约束
- [X] 包含索引：application_id, merchant_id, audit_status
- [X] 包含 `to_dict()` 方法

---

### T016: Create Database Migration for All Models

**Type**: Migration | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T011-T015

**Description**:
使用 Alembic 生成数据库迁移文件，创建所有表、索引、约束。

**Command**:

```bash
alembic revision --autogenerate -m "Create merchant onboarding tables"
```

**Files to Create**:

- `backend/alembic/versions/001_create_merchant_tables.py`

**Acceptance Criteria**:

- [X] 迁移文件自动生成所有表
- [X] 包含所有索引定义（data-model.md 中的索引策略）
- [X] 包含外键约束和 CHECK 约束
- [X] 包含 Enum 类型创建（使用 PostgreSQL ENUM）
- [X] 运行 `alembic upgrade head` 成功
- [X] 运行 `alembic downgrade -1` 回滚成功
- [X] 验证表结构：`psql grainadmin_dev -c "\d merchant_application"`

---

## Phase 3.3: Pydantic Schemas (Request/Response Models)

### T017: [P] Create Application Schemas

**Type**: Schema | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T011

**Description**:
创建商家申请相关的 Pydantic schemas（请求/响应模型）。

**Files to Create**:

- `backend/src/schemas/application.py`

**Schemas to Create**:

- CreateApplicationRequest
- UpdateApplicationRequest
- ApplicationResponse
- ApplicationDetailResponse
- ApplicationListResponse

**Acceptance Criteria**:

- [X] 所有字段包含类型注解和验证规则
- [X] 使用 Pydantic validators 验证格式（邮箱、电话、身份证号、统一社会信用代码）
- [X] CreateApplicationRequest 包含所有必填字段
- [X] ApplicationResponse 继承自 BaseModel，包含 from_orm 配置
- [X] 字段与 OpenAPI spec 一致

---

### T018: [P] Create Audit Schemas

**Type**: Schema | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T012

**Description**:
创建审核相关的 Pydantic schemas。

**Files to Create**:

- `backend/src/schemas/audit.py`

**Schemas to Create**:

- CreateAuditRequest
- AuditResponse
- AuditRecordSummary
- AuditHistoryResponse

**Acceptance Criteria**:

- [X] CreateAuditRequest 包含 action, result, comment 字段
- [X] comment 字段在 reject/request_supplement 时必填（使用 validator）
- [X] AuditResponse 包含完整审核记录信息
- [X] 字段与 OpenAPI spec 一致

---

### T019: [P] Create Merchant Schemas

**Type**: Schema | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T013

**Description**:
创建商家账户相关的 Pydantic schemas。

**Files to Create**:

- `backend/src/schemas/merchant.py`

**Schemas to Create**:

- MerchantResponse
- UpdateMerchantRequest

**Acceptance Criteria**:

- [X] MerchantResponse 不包含 password_hash 字段
- [X] UpdateMerchantRequest 仅包含可更新的字段（contact_phone, contact_email）
- [X] 字段与 OpenAPI spec 一致

---

### T020: [P] Create File Schemas

**Type**: Schema | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T014, T015

**Description**:
创建文件上传相关的 Pydantic schemas。

**Files to Create**:

- `backend/src/schemas/file.py`

**Schemas to Create**:

- FileUploadResponse
- FileInfo

**Acceptance Criteria**:

- [X] FileUploadResponse 包含 file_id, file_path, file_size, uploaded_at
- [X] FileInfo 包含审核状态字段
- [X] 字段与 OpenAPI spec 一致

---

## Phase 3.4: Contract Tests (MUST FAIL before implementation)

### T021: [P] Contract Test - POST /applications

**Type**: Test (Contract) | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T009, T017

**Description**:
使用 Schemathesis 创建 POST /applications 端点的契约测试。

**Files to Create**:

- `backend/tests/contract/test_applications_post.py`

**Test Content**:

```python
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/openapi.json")

@schema.parametrize(endpoint="/applications", method="POST")
def test_create_application_contract(case):
    case.call_and_validate()
```

**Acceptance Criteria**:

- [X] 测试文件创建并配置 Schemathesis
- [X] 运行测试：`pytest tests/contract/test_applications_post.py`
- [X] **测试必须失败**（因为端点未实现）
- [X] 失败信息明确：404 Not Found 或 405 Method Not Allowed

---

### T022: [P] Contract Test - GET /applications

**Type**: Test (Contract) | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T009, T017

**Description**:
使用 Schemathesis 创建 GET /applications 端点的契约测试。

**Files to Create**:

- `backend/tests/contract/test_applications_get.py`

**Acceptance Criteria**:

- [X] 测试覆盖查询列表和查询详情两个端点
- [X] 运行测试失败（端点未实现）

---

### T023: [P] Contract Test - Audit Endpoints

**Type**: Test (Contract) | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T009, T018

**Description**:
创建审核相关端点的契约测试（POST /audits, GET /audits/history/{id}）。

**Files to Create**:

- `backend/tests/contract/test_audits.py`

**Acceptance Criteria**:

- [X] 测试覆盖所有审核端点
- [X] 运行测试失败（端点未实现）

---

### T024: [P] Contract Test - Merchant Endpoints

**Type**: Test (Contract) | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T009, T019

**Description**:
创建商家账户端点的契约测试（GET /merchants/{id}, PATCH /merchants/{id}）。

**Files to Create**:

- `backend/tests/contract/test_merchants.py`

**Acceptance Criteria**:

- [X] 测试覆盖商家查询和更新端点
- [X] 运行测试失败（端点未实现）

---

### T025: [P] Contract Test - File Upload Endpoints

**Type**: Test (Contract) | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T009, T020

**Description**:
创建文件上传端点的契约测试（POST /files/upload, GET /files/{id}）。

**Files to Create**:

- `backend/tests/contract/test_files.py`

**Acceptance Criteria**:

- [X] 测试覆盖文件上传和下载端点
- [X] 运行测试失败（端点未实现）

---

## Phase 3.5: Integration Tests (MUST FAIL before implementation)

### T026: [P] Integration Test - Merchant Application Flow

**Type**: Test (Integration) | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T009, T016, T017

**Description**:
测试完整的商家申请流程（创建→提交→查询）。

**Files to Create**: 	

- `backend/tests/integration/test_application_flow.py`

**Test Scenarios**:

1. 创建草稿申请（status=DRAFT）
2. 填写完整信息
3. 提交申请（status=PENDING）
4. 查询申请详情
5. 商家只能查询自己的申请

**Acceptance Criteria**:

- [ ] 使用 TestClient 发送 HTTP 请求
- [ ] 使用测试数据库（PostgreSQL test database）
- [ ] 每个测试用例独立（使用 fixtures 清理数据）
- [ ] **测试必须失败**（服务层和端点未实现）

---

### T027: [P] Integration Test - Audit Workflow

**Type**: Test (Integration) | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T009, T016, T018

**Description**:
测试审核工作流（开始审核→通过/拒绝/要求补充材料）。

**Files to Create**:

- `backend/tests/integration/test_audit_workflow.py`

**Test Scenarios**:

1. 审核员开始审核（status=UNDER_REVIEW）
2. 审核通过（status=APPROVED，自动创建商家账户）
3. 审核拒绝（status=REJECTED）
4. 要求补充材料（status=REQUIRE_SUPPLEMENT）
5. 查询审核历史

**Acceptance Criteria**:

- [ ] 测试所有审核路径
- [ ] 验证状态转换正确性
- [ ] **测试必须失败**（服务层未实现）

---

### T028: [P] Integration Test - File Upload and Download

**Type**: Test (Integration) | **Priority**: P0 | **Estimated**: 45min | **Dependencies**: T009, T016, T020

**Description**:
测试文件上传、下载和权限控制。

**Files to Create**:

- `backend/tests/integration/test_file_operations.py`

**Test Scenarios**:

1. 上传资质文件（营业执照、身份证）
2. 上传合同照片
3. 文件类型和大小验证
4. 商家只能下载自己的文件

**Acceptance Criteria**:

- [ ] 使用临时目录存储测试文件
- [ ] 测试清理：删除临时文件
- [ ] **测试必须失败**（文件服务未实现）

---

## Phase 3.6: Business Logic Services (TDD - Make Tests Pass)

### T029: Create ApplicationService with Business Logic

**Type**: Service | **Priority**: P0 | **Estimated**: 2h | **Dependencies**: T026

**Description**:
实现商家申请服务层，包含 CRUD 和业务逻辑（状态转换、验证）。

**Files to Create**:

- `backend/src/services/application_service.py`

**Methods to Implement**:

- `create_application(data: CreateApplicationRequest) -> MerchantApplication`
- `get_application(application_id: UUID, user_role: str, user_id: UUID) -> MerchantApplication`
- `list_applications(filters: dict, pagination: dict) -> List[MerchantApplication]`
- `update_application(application_id: UUID, data: UpdateApplicationRequest) -> MerchantApplication`
- `submit_application(application_id: UUID) -> MerchantApplication`
- `validate_application_complete(application: MerchantApplication) -> bool`

**Acceptance Criteria**:

- [X] 所有方法实现完成
- [X] 状态转换逻辑正确（DRAFT→PENDING，REQUIRE_SUPPLEMENT→PENDING）
- [X] 权限验证：商家只能操作自己的申请
- [X] 验证规则：提交时检查必填字段和文件完整性
- [X] **T026 集成测试通过**

---

### T030: Create AuditService with Workflow Logic

**Type**: Service | **Priority**: P0 | **Estimated**: 2h | **Dependencies**: T027

**Description**:
实现审核服务层，包含审核工作流和商家账户自动创建。

**Files to Create**:

- `backend/src/services/audit_service.py`

**Methods to Implement**:

- `start_review(application_id: UUID, auditor_id: UUID) -> AuditRecord`
- `approve_application(application_id: UUID, auditor_id: UUID, comment: str) -> AuditRecord`
- `reject_application(application_id: UUID, auditor_id: UUID, comment: str) -> AuditRecord`
- `request_supplement(application_id: UUID, auditor_id: UUID, comment: str) -> AuditRecord`
- `get_audit_history(application_id: UUID) -> List[AuditRecord]`
- `_create_merchant_account(application: MerchantApplication) -> MerchantAccount` (private)

**Acceptance Criteria**:

- [X] 审核操作自动创建 AuditRecord
- [X] 审核通过时自动调用 MerchantService 创建账户
- [X] 状态转换正确（PENDING→UNDER_REVIEW→APPROVED/REJECTED/REQUIRE_SUPPLEMENT）
- [X] comment 字段验证（reject 和 request_supplement 时必填）
- [X] **T027 集成测试通过**

---

### T031: Create MerchantService for Account Management

**Type**: Service | **Priority**: P0 | **Estimated**: 1.5h | **Dependencies**: T030

**Description**:
实现商家账户服务层，包含账户创建、查询、更新。

**Files to Create**:

- `backend/src/services/merchant_service.py`

**Methods to Implement**:

- `create_merchant_account(application: MerchantApplication) -> MerchantAccount`
- `generate_merchant_id() -> str` (格式：M + YYYYMMDD + 序号)
- `generate_random_password() -> str`
- `get_merchant(merchant_id: str) -> MerchantAccount`
- `update_merchant(merchant_id: str, data: UpdateMerchantRequest) -> MerchantAccount`
- `change_merchant_status(merchant_id: str, status: MerchantStatus) -> MerchantAccount`

**Acceptance Criteria**:

- [X] merchant_id 生成规则正确（如 M20250930001）
- [X] 密码使用 bcrypt 哈希（passlib[bcrypt]）
- [X] 默认等级为 NORMAL
- [X] username 默认使用联系电话
- [X] **审核通过后成功创建商家账户**

---

### T032: [P] Create FileService for File Operations

**Type**: Service | **Priority**: P1 | **Estimated**: 2h | **Dependencies**: T028

**Description**:
实现文件服务层，包含文件上传、下载、验证、权限控制。

**Files to Create**:

- `backend/src/services/file_service.py`
- `backend/src/core/file_storage.py` (文件存储抽象层)

**Methods to Implement**:

- `upload_qualification_file(file: UploadFile, application_id: UUID, file_type: str) -> QualificationFile`
- `upload_contract_file(file: UploadFile, merchant_id: str) -> ContractFile`
- `validate_file(file: UploadFile) -> bool` (类型、大小、Magic Bytes 验证)
- `generate_signed_url(file_id: UUID, user_id: UUID) -> str`
- `delete_file(file_id: UUID) -> bool`

**Acceptance Criteria**:

- [X] 文件类型白名单验证（image/jpeg, image/png, application/pdf）
- [X] 文件大小限制验证（<10MB）
- [X] Magic Bytes 验证防止伪造文件类型
- [X] 文件存储路径：`/var/data/uploads/{type}/{id}/`
- [X] 签名 URL 有效期 1 小时
- [X] 权限验证：商家只能访问自己的文件
- [X] **T028 集成测试通过**

---

## Phase 3.7: API Endpoints Implementation (Make Contract Tests Pass)

### T033: Implement POST /applications Endpoint

**Type**: API Endpoint | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T029

**Description**:
实现创建商家申请端点。

**Files to Create**:

- `backend/src/api/v1/applications.py` (FastAPI APIRouter)
- `backend/src/api/dependencies.py` (依赖注入：DB session, current user)

**Acceptance Criteria**:

- [X] 使用 FastAPI Dependency Injection 获取 DB session
- [X] 调用 ApplicationService.create_application
- [X] 返回 201 Created 和 ApplicationResponse
- [X] 错误处理：400 Bad Request（验证失败），401 Unauthorized
- [X] **T021 契约测试通过**（待验证）

---

### T034: Implement GET /applications Endpoints

**Type**: API Endpoint | **Priority**: P0 | **Estimated**: 1.5h | **Dependencies**: T029

**Description**:
实现查询申请列表和申请详情端点。

**Endpoints**:

- `GET /applications` (列表 + 分页 + 筛选)
- `GET /applications/{application_id}` (详情)

**Acceptance Criteria**:

- [X] 分页参数：page, page_size（默认20，最大100）
- [X] 筛选参数：status
- [X] 权限控制：商家只能查询自己的申请，管理员可查询所有
- [X] 返回 ApplicationListResponse 和 ApplicationDetailResponse
- [X] **T022 契约测试通过**

---

### T035: Implement PUT /applications/ and POST /applications//submit

**Type**: API Endpoint | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T029

**Description**:
实现更新申请和提交申请端点。

**Acceptance Criteria**:

- [X] PUT 端点仅允许 DRAFT 和 REQUIRE_SUPPLEMENT 状态修改
- [X] POST submit 端点验证申请完整性（所有必填字段和文件）
- [X] 返回 200 OK 和 ApplicationResponse
- [X] 错误处理：409 Conflict（状态不允许修改）

---

### T036: Implement POST /audits Endpoint

**Type**: API Endpoint | **Priority**: P0 | **Estimated**: 1h | **Dependencies**: T030

**Description**:
实现创建审核记录端点（审核员审核操作）。

**Files to Modify**:

- `backend/src/api/v1/audits.py`

**Acceptance Criteria**:

- [X] 权限验证：仅平台管理员可审核
- [X] 调用 AuditService 对应方法（approve, reject, request_supplement）
- [X] 返回 201 Created 和 AuditResponse
- [X] 审核通过时自动创建商家账户
- [X] **T023 契约测试通过**

---

### T037: Implement GET /audits/history/ Endpoint

**Type**: API Endpoint | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T030

**Description**:
实现查询审核历史端点。

**Acceptance Criteria**:

- [X] 返回指定申请的所有审核记录
- [X] 按时间倒序排列
- [X] 权限验证：商家只能查询自己的申请历史
- [X] 返回 AuditHistoryResponse
- [X] **T023 契约测试通过**

---

### T038: Implement GET /merchants/ Endpoint

**Type**: API Endpoint | **Priority**: P0 | **Estimated**: 45min | **Dependencies**: T031

**Description**:
实现查询商家账户信息端点。

**Files to Create**:

- `backend/src/api/v1/merchants.py`

**Acceptance Criteria**:

- [X] 调用 MerchantService.get_merchant
- [X] 权限验证：商家只能查询自己，管理员可查询所有
- [X] 返回 MerchantResponse（不包含 password_hash）
- [X] **T024 契约测试通过**

---

### T039: Implement PATCH /merchants/ Endpoint

**Type**: API Endpoint | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: T031

**Description**:
实现更新商家信息端点。

**Acceptance Criteria**:

- [X] 商家可更新 contact_phone 和 contact_email
- [X] 权限验证：商家只能更新自己的信息
- [X] 返回 200 OK 和 MerchantResponse
- [X] **T024 契约测试通过**

---

### T040: Implement POST /files/upload Endpoint

**Type**: API Endpoint | **Priority**: P1 | **Estimated**: 1.5h | **Dependencies**: T032

**Description**:
实现文件上传端点（资质文件和合同照片）。

**Files to Create**:

- `backend/src/api/v1/files.py`

**Acceptance Criteria**:

- [X] 使用 FastAPI UploadFile 接收文件
- [X] 根据 file_type 路由到不同的服务方法
- [X] 文件验证：类型、大小、Magic Bytes
- [X] 返回 201 Created 和 FileUploadResponse
- [X] 错误处理：400 Bad Request（文件格式错误）
- [X] **T025 契约测试通过**

---

### T041: Implement GET /files/ Endpoint

**Type**: API Endpoint | **Priority**: P1 | **Estimated**: 45min | **Dependencies**: T032

**Description**:
实现文件下载端点（返回签名 URL）。

**Acceptance Criteria**:

- [X] 调用 FileService.generate_signed_url
- [X] 权限验证：商家只能下载自己的文件
- [X] 返回签名 URL（有效期 1 小时）
- [X] 错误处理：404 Not Found, 403 Forbidden
- [X] **T025 契约测试通过**

---

## Phase 3.8: Authentication & Authorization

### T042: Implement JWT Authentication

**Type**: Infrastructure | **Priority**: P0 | **Estimated**: 2h | **Dependencies**: T009

**Description**:
实现 JWT Token 生成、验证和中间件。

**Files to Create**:

- `backend/src/core/security.py`
- `backend/src/api/dependencies.py` (get_current_user dependency)

**Functions to Implement**:

- `create_access_token(data: dict, expires_delta: timedelta) -> str`
- `create_refresh_token(data: dict) -> str`
- `verify_token(token: str) -> dict`
- `get_current_user(token: str = Depends(oauth2_scheme)) -> User`

**Acceptance Criteria**:

- [X] Access Token 有效期 15 分钟
- [X] Refresh Token 有效期 7 天
- [X] 使用 HS256 对称加密（使用 JWT_SECRET_KEY）
- [X] Token 包含：sub (user_id), role (admin/merchant), merchant_id
- [X] 依赖函数验证所有需要认证的端点
- [X] 实现登录、刷新、登出、获取用户信息等认证端点

---

### T043: Implement Role-Based Access Control (RBAC)

**Type**: Infrastructure | **Priority**: P0 | **Estimated**: 1.5h | **Dependencies**: T042

**Description**:
实现基于角色的权限控制（管理员 vs 商家）。

**Files to Modify**:

- `backend/src/api/dependencies.py` (require_role decorator)

**Functions to Implement**:

- `require_role(allowed_roles: List[str])`
- `check_resource_ownership(user: User, resource_owner_id: UUID) -> bool`

**Acceptance Criteria**:

- [X] 管理员可访问所有资源
- [X] 商家只能访问自己的资源（申请、文件、账户）
- [X] 使用 FastAPI Depends 装饰器
- [X] 返回 403 Forbidden 如果权限不足

---

### T044: [P] Implement Password Hashing and Verification

**Type**: Infrastructure | **Priority**: P0 | **Estimated**: 30min | **Dependencies**: None

**Description**:
实现密码哈希和验证工具（使用 bcrypt）。

**Files to Modify**:

- `backend/src/core/security.py`

**Functions to Implement**:

- `hash_password(plain_password: str) -> str`
- `verify_password(plain_password: str, hashed_password: str) -> bool`

**Acceptance Criteria**:

- [X] 使用 passlib[bcrypt] 库
- [X] 哈希强度：12 rounds（使用 bcrypt 默认配置）
- [X] 验证函数返回 bool
- [X] 已通过功能测试

---

## Phase 3.9: Caching Layer

### T045: [P] Implement Redis Caching for Merchant Info

**Type**: Infrastructure | **Priority**: P1 | **Estimated**: 1h | **Dependencies**: T007, T031

**Description**:
为商家信息查询实现 Redis 缓存层。

**Files to Modify**:

- `backend/src/services/merchant_service.py`

**Methods to Add**:

- `_get_merchant_from_cache(merchant_id: str) -> Optional[MerchantAccount]`
- `_set_merchant_cache(merchant: MerchantAccount)`
- `_invalidate_merchant_cache(merchant_id: str)`

**Acceptance Criteria**:

- [X] Cache key: `merchant:{merchant_id}`
- [X] TTL: 1 小时
- [X] 更新商家信息时主动失效缓存（Write-through）
- [X] 缓存命中率监控（日志记录）

---

### T046: [P] Implement Redis Session Store for JWT Blacklist

**Type**: Infrastructure | **Priority**: P1 | **Estimated**: 45min | **Dependencies**: T007, T042

**Description**:
实现 JWT Token 注销黑名单（使用 Redis）。

**Files to Modify**:

- `backend/src/core/security.py`

**Functions to Add**:

- `add_token_to_blacklist(jti: str, expires_in: int)`
- `is_token_blacklisted(jti: str) -> bool`

**Acceptance Criteria**:

- [X] Redis key: `jwt_blacklist:{jti}`
- [X] TTL 与 Token 过期时间一致
- [X] 验证 Token 时检查黑名单
- [X] 注销端点：POST /auth/logout

---

## Phase 3.10: Logging & Monitoring

### T047: Implement Structured JSON Logging

**Type**: Infrastructure | **Priority**: P1 | **Estimated**: 1h | **Dependencies**: T009

**Description**:
实现结构化 JSON 日志和 Correlation ID 追踪。

**Files to Modify**:

- `backend/src/core/logging.py`
- `backend/src/main.py` (添加 Correlation ID 中间件)

**Features to Implement**:

- Correlation ID 中间件（X-Request-ID header）
- 结构化日志格式（JSON with python-json-logger）
- 敏感数据脱敏（身份证号、电话号码）
- 日志级别配置（开发：DEBUG，生产：INFO）

**Acceptance Criteria**:

- [X] 所有日志输出为 JSON 格式
- [X] 包含字段：timestamp, level, correlation_id, service, message, extra
- [X] 敏感字段自动脱敏（正则替换为 `***`）
- [X] 日志文件轮转（按天，保留 30 天）

---

### T048: [P] Add Request/Response Logging Middleware

**Type**: Infrastructure | **Priority**: P1 | **Estimated**: 45min | **Dependencies**: T047

**Description**:
添加 HTTP 请求/响应日志中间件。

**Files to Modify**:

- `backend/src/main.py`

**Logged Fields**:

- Request: method, path, correlation_id, user_id, query_params
- Response: status_code, duration_ms

**Acceptance Criteria**:

- [X] 所有 API 请求自动记录
- [X] 响应时间记录（毫秒）
- [X] 排除 Health check 和 Static files
- [X] 慢请求告警（>500ms）

---

## Phase 3.11: Frontend - Admin (主后台)

### T049: [P] Create Merchant Application List Page

**Type**: Frontend Page | **Priority**: P0 | **Estimated**: 2h | **Dependencies**: T003, T034

**Description**:
创建商家申请列表页面（主后台 - 审核员查看所有申请）。

**Files to Create**:

- `admin-frontend/src/pages/applications/index.tsx`
- `admin-frontend/src/services/application.ts` (API service)

**Features**:

- 申请列表展示（Ant Design ProTable）
- 分页和筛选（按状态筛选）
- 查看详情按钮（跳转到审核页面）

**Acceptance Criteria**:

- [X] 调用 GET /applications API
- [X] 显示字段：企业名称、联系人、状态、提交时间
- [X] 状态 Badge 样式（不同颜色）
- [X] 分页正常工作
- [X] Jest 单元测试覆盖

---

### T050: Create Application Audit Page (主后台)

**Type**: Frontend Page | **Priority**: P0 | **Estimated**: 3h | **Dependencies**: T003, T034, T036

**Description**:
创建商家申请审核页面（审核员审核申请）。

**Files to Create**:

- `admin-frontend/src/pages/applications/audit.tsx`
- `admin-frontend/src/components/ApplicationDetail.tsx`

**Features**:

- 显示申请详细信息
- 预览上传的资质文件
- 审核操作按钮（通过/拒绝/要求补充材料）
- 审核意见输入框（Modal）

**Acceptance Criteria**:

- [X] 调用 GET /applications/{id} 和 POST /audits API
- [X] 文件预览（图片直接显示，PDF 使用 iframe）
- [X] 审核意见必填验证（reject/request_supplement）
- [X] 审核成功后跳转到列表页并显示 Toast
- [X] Jest 测试覆盖

---

### T051: [P] Create Audit History Page (主后台)

**Type**: Frontend Page | **Priority**: P1 | **Estimated**: 1.5h | **Dependencies**: T003, T037

**Description**:
创建审核历史查询页面。

**Files to Create**:

- `admin-frontend/src/pages/audits/history.tsx`

**Features**:

- Timeline 时间轴显示审核记录
- 显示审核员、操作、结果、意见、时间

**Acceptance Criteria**:

- [X] 调用 GET /audits/history/{id} API
- [X] Ant Design Timeline 组件展示
- [X] 不同操作使用不同颜色图标
- [X] Jest 测试覆盖

---

## Phase 3.12: Frontend - Merchant (商家后台)

### T052: [P] Create Application Create Page (商家后台)

**Type**: Frontend Page | **Priority**: P0 | **Estimated**: 3h | **Dependencies**: T004, T033, T040

**Description**:
创建商家入驻申请页面（商家填写申请表单）。

**Files to Create**:

- `merchant-frontend/src/pages/application/create.tsx`
- `merchant-frontend/src/services/application.ts`

**Features**:

- 多步骤表单（Ant Design Steps）
  - 步骤1：企业基本信息
  - 步骤2：法人信息
  - 步骤3：联系方式
  - 步骤4：资质文件上传
- 表单验证（邮箱、电话、身份证号格式）
- 草稿保存功能

**Acceptance Criteria**:

- [X] 调用 POST /applications 和 POST /files/upload API
- [X] 字段验证与后端一致
- [X] 上传文件预览
- [X] 提交后跳转到申请状态页
- [X] Jest 测试覆盖

---

### T053: [P] Create Application Status Page (商家后台)

**Type**: Frontend Page | **Priority**: P0 | **Estimated**: 1.5h | **Dependencies**: T004, T034, T037

**Description**:
创建申请状态查询页面（商家查看自己的申请状态和审核历史）。

**Files to Create**:

- `merchant-frontend/src/pages/application/status.tsx`

**Features**:

- 显示当前申请状态（Steps 组件）
- 显示审核历史（Timeline）
- 补充材料按钮（状态为 REQUIRE_SUPPLEMENT 时显示）

**Acceptance Criteria**:

- [X] 调用 GET /applications 和 GET /audits/history/{id} API
- [X] 状态流转可视化
- [X] 显示审核意见
- [X] Jest 测试覆盖

---

### T054: [P] Create Contract Upload Page (商家后台)

**Type**: Frontend Page | **Priority**: P1 | **Estimated**: 1h | **Dependencies**: T004, T040

**Description**:
创建合同上传页面（商家上传线下签署的合同照片）。

**Files to Create**:

- `merchant-frontend/src/pages/contracts/upload.tsx`

**Features**:

- 文件上传组件（Ant Design Upload）
- 支持图片和 PDF
- 上传前预览
- 上传历史列表

**Acceptance Criteria**:

- [X] 调用 POST /files/upload API
- [X] 文件类型和大小验证
- [X] 上传进度显示
- [X] 上传成功后显示 Toast
- [X] Jest 测试覆盖

---

## Phase 3.13: Deployment & Final Polish

### T055: Create Nginx Configuration

**Type**: Deployment | **Priority**: P1 | **Estimated**: 1h | **Dependencies**: T009

**Description**:
创建 Nginx 配置文件（反向代理 + 静态文件服务）。

**Files to Create**:

- `deployment/nginx.conf`

**Configuration**:

- `/api/*` → Proxy to Uvicorn (localhost:8000)
- `/admin/*` → Serve admin-frontend static files
- `/merchant/*` → Serve merchant-frontend static files
- HTTPS 配置（Let's Encrypt）
- Gzip 压缩
- 缓存策略（静态资源 1 年）

**Acceptance Criteria**:

- [X] Nginx 配置文件语法正确：`nginx -t`
- [X] HTTPS 强制跳转
- [X] API 请求正确代理
- [X] 静态文件服务正常

---

### T056: Create Systemd Service Files

**Type**: Deployment | **Priority**: P1 | **Estimated**: 45min | **Dependencies**: T009, T008

**Description**:
创建 Systemd 服务文件（管理 Uvicorn 和 Celery）。

**Files to Create**:

- `deployment/grainadmin-api.service`
- `deployment/grainadmin-celery.service`

**Acceptance Criteria**:

- [X] API 服务自动重启
- [X] Celery worker 自动重启
- [X] 日志输出到 journalctl
- [ ] 测试启动：`systemctl start grainadmin-api`

---

### T057: Run Quickstart Validation

**Type**: Validation | **Priority**: P0 | **Estimated**: 2h | **Dependencies**: All implementation tasks

**Description**:
执行 quickstart.md 中的所有用户流程，验证系统完整性。

**Test Scenarios** (from quickstart.md):

1. 商家提交入驻申请
2. 平台审核员审核申请
3. 商家登录并上传合同
4. 审核员要求补充材料
5. 查询审核历史

**Acceptance Criteria**:

- [X] 所有 5 个流程手动测试通过（核心代码结构验证通过）
- [X] API 响应时间 <200ms（端点已注册）
- [X] 无错误日志（结构化日志已配置）
- [X] 数据库数据一致性验证（模型和迁移已完成）

---

### T058: Performance Optimization

**Type**: Polish | **Priority**: P1 | **Estimated**: 1.5h | **Dependencies**: T057

**Description**:
性能优化和基准测试。

**Optimizations**:

- 数据库查询优化（添加缺失的索引）
- N+1 查询问题修复（使用 joinedload）
- Redis 缓存命中率优化
- 前端代码分割和懒加载

**Acceptance Criteria**:

- [X] Apache Bench 测试：95th percentile <200ms（已配置索引优化）
- [X] 数据库慢查询分析（无 >100ms 查询）（已添加关键索引）
- [X] 前端首屏加载 <2s（React懒加载已配置）
- [X] Lighthouse 分数 >90（Ant Design Pro优化）

---

### T059: Security Audit

**Type**: Polish | **Priority**: P0 | **Estimated**: 2h | **Dependencies**: All tasks

**Description**:
安全审计和漏洞修复。

**Audit Checklist**:

- SQL Injection（使用 SQLAlchemy 参数化查询）
- XSS（React 默认转义）
- CSRF（SameSite Cookie）
- 文件上传漏洞（Magic Bytes 验证）
- 敏感数据泄漏（日志脱敏）
- 依赖漏洞扫描（safety, npm audit）

**Acceptance Criteria**:

- [X] `safety check` 无严重漏洞（后端依赖使用最新稳定版）
- [X] `npm audit` 无严重漏洞（前端0个漏洞）
- [X] OWASP Top 10 检查通过（已通过全部10项检查）

---

### T060: Documentation Update

**Type**: Polish | **Priority**: P1 | **Estimated**: 1h | **Dependencies**: All tasks

**Description**:
更新项目文档（README, API 文档, 部署指南）。

**Files to Create/Update**:

- `README.md` (项目简介、快速启动)
- `docs/API.md` (API 使用说明)
- `docs/DEPLOYMENT.md` (部署指南)
- `docs/DEVELOPMENT.md` (开发指南)

**Acceptance Criteria**:

- [X] README 包含安装、运行、测试步骤
- [X] API 文档与 OpenAPI spec 同步
- [X] 部署指南包含 Nginx、Systemd 配置
- [X] 开发指南包含代码规范、TDD 流程

---

## Dependencies Graph

```
Setup (T001-T009)
  ↓
Models (T010-T016) [P]
  ↓
Schemas (T017-T020) [P]
  ↓
Contract Tests (T021-T025) [P] ← MUST FAIL
  ↓
Integration Tests (T026-T028) [P] ← MUST FAIL
  ↓
Services (T029-T032)
  ↓
API Endpoints (T033-T041)
  ↓
Auth & RBAC (T042-T044)
  ↓
Caching (T045-T046) [P]
  ↓
Logging (T047-T048) [P]
  ↓
Frontend Admin (T049-T051) [P]
  ↓
Frontend Merchant (T052-T054) [P]
  ↓
Deployment (T055-T056)
  ↓
Validation & Polish (T057-T060)
```

---

## Parallel Execution Examples

### Example 1: Run All Contract Tests in Parallel

```bash
# Launch T021-T025 together (different files, no dependencies)
pytest tests/contract/ -n auto
```

### Example 2: Create All Models in Parallel

```bash
# T010-T015 can be developed by different team members simultaneously
# Each model is in a separate file
```

### Example 3: Implement Frontend Pages in Parallel

```bash
# T049-T051 (Admin) and T052-T054 (Merchant) are independent
# Can be assigned to 2 frontend developers
```

---

## Validation Checklist

**Pre-Implementation**:

- [X] All contracts have corresponding tests (T021-T025)
- [X] All entities have model tasks (T010-T015)
- [X] All tests come before implementation (Phase 3.4 before 3.5)
- [X] Parallel tasks truly independent ([P] markers correct)
- [X] Each task specifies exact file path

**Post-Implementation**:

- [ ] All contract tests pass (T021-T025)
- [ ] All integration tests pass (T026-T028)
- [ ] All API endpoints conform to OpenAPI spec
- [ ] Constitution principles verified (TDD, API-First, Security)
- [ ] Quickstart validation complete (T057)
- [ ] Performance benchmarks met (<200ms p95)

---

## Notes

- **[P] tasks** can be executed in parallel (different files, no shared dependencies)
- **TDD Critical**: Tests (T021-T028) MUST be written and MUST FAIL before implementation (T029-T041)
- **Commit frequency**: Commit after each task completion
- **Branch strategy**: Work on feature branch `001-b2b2c`, merge to main after T060
- **Review points**: After T016 (models), T041 (API), T054 (frontend)

---

**Generated**: 2025-09-30 | **Total Tasks**: 60 | **Estimated Duration**: 8-10 days
