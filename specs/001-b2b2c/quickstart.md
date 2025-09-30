# Quickstart Guide: 商家入驻管理系统

**Feature**: 001-b2b2c | **Date**: 2025-09-30
**Purpose**: 验证系统核心功能的快速启动和测试指南

---

## Prerequisites

### Required Software
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Git

### Environment Setup

```bash
# 1. Clone repository (假设已存在)
cd /path/to/grainAdminPro

# 2. 安装后端依赖
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和 Redis 连接

# 4. 初始化数据库
createdb grainadmin_dev
alembic upgrade head

# 5. 安装前端依赖（主后台）
cd ../admin-frontend
npm install

# 6. 安装前端依赖（商家后台）
cd ../merchant-frontend
npm install
```

---

## Start Services

### 1. Start Backend API

```bash
cd backend
source venv/bin/activate

# Development mode (with auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 验证 API 运行
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 2. Start Celery Worker (Optional for async tasks)

```bash
cd backend
source venv/bin/activate

celery -A src.celery_app worker -l info
```

### 3. Start Admin Frontend

```bash
cd admin-frontend
npm run dev

# Access at: http://localhost:8001
```

### 4. Start Merchant Frontend

```bash
cd merchant-frontend
npm run dev

# Access at: http://localhost:8002
```

---

## Core User Flows

### Flow 1: 商家提交入驻申请

**Goal**: 商家填写并提交入驻申请

**Steps**:

1. **访问商家后台**
   ```
   URL: http://localhost:8002/application/create
   ```

2. **填写申请表单**
   - 企业名称: "测试科技有限公司"
   - 统一社会信用代码: "91110108MA01234567"
   - 法人姓名: "张三"
   - 法人身份证号: "110101199001011234"
   - 联系人姓名: "李四"
   - 联系电话: "13800138000"
   - 联系邮箱: "contact@test.com"
   - 经营类目: ["食品", "日用品"]

3. **上传资质文件**
   - 营业执照: `business_license.jpg`
   - 身份证正面: `id_card_front.jpg`
   - 身份证背面: `id_card_back.jpg`

4. **提交申请**
   - 点击"提交申请"按钮
   - 系统验证表单和文件完整性
   - 申请状态变更为 `PENDING`

**Expected Result**:
```json
{
  "id": "uuid",
  "business_name": "测试科技有限公司",
  "status": "pending",
  "submitted_at": "2025-09-30T10:30:00Z"
}
```

**API Trace**:
```bash
POST /api/v1/applications
POST /api/v1/files/upload (x3)
POST /api/v1/applications/{id}/submit
```

---

### Flow 2: 平台审核员审核申请

**Goal**: 平台管理员审核商家申请并通过

**Steps**:

1. **登录主后台**
   ```
   URL: http://localhost:8001/login
   Username: admin@grainadmin.com
   Password: admin123 (测试账号)
   ```

2. **查看待审核申请**
   ```
   URL: http://localhost:8001/applications?status=pending
   ```
   - 看到商家申请列表
   - 点击申请查看详情

3. **审核申请**
   - 查看申请信息和上传的资质文件
   - 点击"开始审核"按钮（状态变更为 `UNDER_REVIEW`）
   - 验证营业执照号码和身份证号码
   - 选择"审核通过"

4. **填写审核意见**
   - 审核意见: "资质齐全，审核通过"
   - 点击"提交审核结果"

5. **系统自动创建商家账户**
   - 生成商家编号: `M20250930001`
   - 生成登录凭证（用户名: 13800138000, 密码: 随机生成）
   - 发送登录凭证到商家邮箱（未来功能）

**Expected Result**:
```json
{
  "audit_record": {
    "id": "uuid",
    "application_id": "uuid",
    "auditor_name": "管理员",
    "action": "approve",
    "result": "approved",
    "comment": "资质齐全，审核通过"
  },
  "merchant_account": {
    "merchant_id": "M20250930001",
    "username": "13800138000",
    "level": "normal",
    "status": "active"
  }
}
```

**API Trace**:
```bash
GET /api/v1/applications?status=pending
GET /api/v1/applications/{id}
POST /api/v1/audits (action: start_review)
POST /api/v1/audits (action: approve)
POST /api/v1/merchants (自动创建)
```

---

### Flow 3: 商家登录并上传合同

**Goal**: 商家使用新账户登录并上传线下合同照片

**Steps**:

1. **商家登录**
   ```
   URL: http://localhost:8002/login
   Username: 13800138000
   Password: (系统发送的临时密码)
   ```
   - 首次登录强制修改密码

2. **查看商家信息**
   ```
   URL: http://localhost:8002/profile
   ```
   - 查看商家编号: `M20250930001`
   - 查看等级: `普通商家`
   - 查看申请状态: `已通过`

3. **上传合同照片**
   ```
   URL: http://localhost:8002/contracts/upload
   ```
   - 选择线下签署的合同照片（JPG/PNG/PDF）
   - 点击"上传合同"
   - 系统存储合同并关联到商家账户

**Expected Result**:
```json
{
  "file_id": "uuid",
  "merchant_id": "M20250930001",
  "file_path": "/contracts/M20250930001/contract_20250930103000.jpg",
  "file_size": 2048576,
  "uploaded_at": "2025-09-30T10:30:00Z"
}
```

**API Trace**:
```bash
POST /api/v1/auth/login
POST /api/v1/auth/change-password
GET /api/v1/merchants/M20250930001
POST /api/v1/files/upload
```

---

### Flow 4: 审核员要求补充材料

**Goal**: 审核员发现材料不完整，要求商家补充材料

**Steps**:

1. **审核员查看申请**
   - 发现营业执照图片不清晰

2. **要求补充材料**
   - 选择"要求补充材料"
   - 填写原因: "营业执照图片不清晰，请重新上传"
   - 提交审核结果
   - 申请状态变更为 `REQUIRE_SUPPLEMENT`

3. **商家收到补充通知** (未来功能：邮件/站内信)
   - 商家登录查看申请状态
   - 看到补充材料要求

4. **商家重新上传文件**
   - 上传新的营业执照图片
   - 点击"重新提交申请"
   - 申请状态变更回 `PENDING`

5. **审核员重新审核**
   - 查看新上传的文件
   - 审核通过

**Expected Result**:
- 申请经历状态变化: `PENDING` → `UNDER_REVIEW` → `REQUIRE_SUPPLEMENT` → `PENDING` → `APPROVED`
- 审核历史记录完整，包含所有操作

**API Trace**:
```bash
POST /api/v1/audits (action: request_supplement)
GET /api/v1/applications/{id} (商家查看)
POST /api/v1/files/upload (重新上传)
POST /api/v1/applications/{id}/submit (重新提交)
POST /api/v1/audits (action: approve)
```

---

### Flow 5: 查询审核历史

**Goal**: 查看商家申请的完整审核历史

**Steps**:

1. **平台管理员查看审核历史**
   ```
   URL: http://localhost:8001/audits/history/{application_id}
   ```

2. **商家查看自己的审核历史**
   ```
   URL: http://localhost:8002/application/status
   ```

**Expected Result**:
```json
{
  "application_id": "uuid",
  "records": [
    {
      "id": "uuid-1",
      "auditor_name": "管理员",
      "action": "start_review",
      "result": "in_progress",
      "created_at": "2025-09-30T10:00:00Z"
    },
    {
      "id": "uuid-2",
      "auditor_name": "管理员",
      "action": "request_supplement",
      "result": "pending_supplement",
      "comment": "营业执照图片不清晰，请重新上传",
      "created_at": "2025-09-30T10:05:00Z"
    },
    {
      "id": "uuid-3",
      "auditor_name": "管理员",
      "action": "approve",
      "result": "approved",
      "comment": "审核通过",
      "created_at": "2025-09-30T10:30:00Z"
    }
  ]
}
```

---

## Testing Checklist

### Manual Testing

- [ ] **商家申请流程**
  - [ ] 创建草稿申请
  - [ ] 填写完整表单信息
  - [ ] 上传所有必需文件（营业执照、身份证）
  - [ ] 提交申请后状态变更为 `PENDING`
  - [ ] 验证表单字段验证（邮箱格式、电话号码格式、身份证号格式）

- [ ] **审核流程**
  - [ ] 审核员开始审核（状态变更为 `UNDER_REVIEW`）
  - [ ] 审核通过后自动创建商家账户
  - [ ] 审核拒绝后申请状态变更为 `REJECTED`
  - [ ] 要求补充材料后状态变更为 `REQUIRE_SUPPLEMENT`
  - [ ] 商家重新提交后状态变回 `PENDING`

- [ ] **商家账户**
  - [ ] 商家账户自动生成（merchant_id, username, password）
  - [ ] 商家首次登录强制修改密码
  - [ ] 商家可以查看自己的申请状态
  - [ ] 商家可以更新自己的基本信息

- [ ] **合同上传**
  - [ ] 商家上传合同照片（JPG/PNG/PDF）
  - [ ] 文件大小限制验证（最大 10MB）
  - [ ] 文件类型验证（仅允许图片和 PDF）
  - [ ] 合同文件关联到商家账户

- [ ] **审核历史**
  - [ ] 平台管理员可以查看完整审核历史
  - [ ] 商家可以查看自己的审核历史
  - [ ] 审核历史按时间倒序排列

- [ ] **权限控制**
  - [ ] 商家只能查看自己的申请和信息
  - [ ] 平台管理员可以查看所有申请
  - [ ] 未登录用户无法访问需要认证的接口

### Automated Testing (TDD)

#### Contract Tests (Schemathesis)
```bash
cd backend
pytest tests/contract/test_api_contracts.py
```

**Expected**: 所有 API 端点符合 OpenAPI 规范

#### Integration Tests
```bash
cd backend
pytest tests/integration/
```

**Test Coverage**:
- `test_create_application`: 测试创建申请
- `test_submit_application`: 测试提交申请
- `test_audit_application`: 测试审核申请
- `test_create_merchant_account`: 测试自动创建商家账户
- `test_upload_contract_file`: 测试上传合同
- `test_get_audit_history`: 测试查询审核历史

#### Unit Tests
```bash
cd backend
pytest tests/unit/
```

**Test Coverage**:
- `test_application_status_transitions`: 测试申请状态转换逻辑
- `test_merchant_id_generation`: 测试商家编号生成规则
- `test_file_validation`: 测试文件验证逻辑
- `test_permission_checks`: 测试权限验证逻辑

---

## Performance Validation

### Load Testing (Apache Bench)

```bash
# Test: 创建申请接口性能
ab -n 1000 -c 50 -T 'application/json' -p application.json \
   http://localhost:8000/api/v1/applications

# Expected: 95th percentile < 200ms
```

### Database Query Performance

```bash
# 检查慢查询
psql grainadmin_dev -c "SELECT * FROM pg_stat_statements WHERE mean_exec_time > 100 ORDER BY mean_exec_time DESC LIMIT 10;"

# 验证索引使用
psql grainadmin_dev -c "EXPLAIN ANALYZE SELECT * FROM merchant_application WHERE status = 'pending' ORDER BY created_at DESC LIMIT 20;"
```

**Expected**: 所有查询使用正确的索引，无全表扫描

---

## Troubleshooting

### Issue: 数据库连接失败

**Symptom**: `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server`

**Solution**:
1. 检查 PostgreSQL 服务是否运行: `pg_isready`
2. 检查 `.env` 文件中的数据库连接配置
3. 确认数据库 `grainadmin_dev` 已创建

### Issue: Redis 连接失败

**Symptom**: `redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379. Connection refused.`

**Solution**:
1. 启动 Redis: `redis-server` (macOS: `brew services start redis`)
2. 检查 Redis 端口: `redis-cli ping` (Expected: `PONG`)

### Issue: 前端无法连接后端 API

**Symptom**: `Network Error` 或 `CORS Error`

**Solution**:
1. 检查后端 API 是否运行: `curl http://localhost:8000/health`
2. 检查前端配置文件中的 API Base URL（`admin-frontend/.env`, `merchant-frontend/.env`）
3. 确认后端 CORS 配置允许前端域名

### Issue: 文件上传失败

**Symptom**: `413 Request Entity Too Large` 或 `400 Invalid File Type`

**Solution**:
1. 检查文件大小是否超过 10MB
2. 检查文件类型是否为允许的格式（JPG/PNG/PDF）
3. 检查 Nginx 配置中的 `client_max_body_size`（生产环境）

---

## Next Steps

After completing this quickstart:

1. ✅ **Phase 2**: 使用 `/tasks` 命令生成详细任务列表
2. ✅ **Phase 3**: 执行任务列表，实现 TDD 开发流程
3. ✅ **Phase 4**: 部署到 Staging 环境进行完整测试
4. ✅ **Phase 5**: 性能优化和生产环境部署

---

## Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Database Schema**: `specs/001-b2b2c/data-model.md`
- **API Contracts**: `specs/001-b2b2c/contracts/openapi.yaml`
- **Architecture Research**: `specs/001-b2b2c/research.md`

---

**Last Updated**: 2025-09-30