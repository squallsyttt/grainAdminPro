# Research & Technical Decisions: 商家入驻管理系统

**Feature**: 001-b2b2c | **Date**: 2025-09-30

## Overview

本文档记录商家入驻管理系统的技术选型、架构决策和最佳实践研究结果。所有决策基于 Constitution 原则（API-First、单体后端、TDD、性能优先）。

---

## 1. Backend Framework: FastAPI

### Decision
使用 **FastAPI** (Python 3.11+) 作为后端 API 框架

### Rationale
1. **性能优越**: 基于 Starlette + Pydantic，异步支持，性能接近 Node.js/Go
2. **自动 OpenAPI 文档**: 原生支持 OpenAPI 3.0 规范生成，符合 API-First 原则
3. **类型安全**: Pydantic 模型提供运行时类型验证和 IDE 自动补全
4. **异步原生**: 支持 async/await，便于集成 Celery 异步任务和高并发处理
5. **生态成熟**: SQLAlchemy ORM、Alembic 迁移、pytest 测试工具链完整

### Alternatives Considered
- **Django REST Framework**: 功能完整但同步架构，性能不如 FastAPI，过于重量级
- **Flask**: 轻量但缺少异步支持和原生 OpenAPI 生成，需要额外插件

### Implementation Notes
- 使用 FastAPI Dependency Injection 管理数据库 Session 和认证
- 通过 `APIRouter` 组织 API 版本（v1, v2）
- Pydantic schemas 定义请求/响应模型，自动生成 OpenAPI 文档

---

## 2. Database: PostgreSQL + SQLAlchemy

### Decision
- **主数据库**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0 (async support)
- **迁移工具**: Alembic

### Rationale
1. **ACID 保证**: 商家申请、审核流程需要强一致性事务支持
2. **JSON 字段**: 支持 JSONB 类型存储灵活的扩展信息（如动态表单字段）
3. **全文搜索**: 内置 tsvector 支持商家名称、经营类目搜索
4. **索引优化**: 支持复合索引、部分索引、GIN 索引（JSON 字段）
5. **SQLAlchemy 2.0**: 原生异步支持，类型提示友好，与 FastAPI 配合默契

### Schema Design Principles
- 每个表包含 `created_at`, `updated_at` 审计字段
- 商家数据通过 `merchant_id` 隔离（多租户）
- 使用 `Enum` 类型管理状态字段（申请状态、商家状态）

### Index Strategy
```sql
-- 商家申请表关键索引
CREATE INDEX idx_merchant_application_status ON merchant_application(status, created_at);
CREATE INDEX idx_merchant_application_merchant_id ON merchant_application(merchant_id);
CREATE INDEX idx_merchant_application_created_at ON merchant_application(created_at DESC);

-- 审核记录索引
CREATE INDEX idx_audit_record_application_id ON audit_record(application_id, created_at);
CREATE INDEX idx_audit_record_auditor_id ON audit_record(auditor_id);

-- 商家账户索引
CREATE INDEX idx_merchant_account_level ON merchant_account(level, status);
```

---

## 3. Caching Strategy: Redis

### Decision
使用 **Redis 6+** 作为多层缓存和 Session 存储

### Rationale
1. **Session 存储**: JWT Token 黑名单（注销 Token）和 Refresh Token 存储
2. **应用缓存**: 商家信息、等级配置、审核员权限数据
3. **分布式锁**: 防止重复提交商家申请（基于 `SET NX EX` 实现）
4. **性能优化**: 商家列表、审核历史等高频查询缓存，降低数据库压力

### Cache Patterns
```python
# 商家信息缓存 (TTL: 1小时)
key: "merchant:{merchant_id}"
value: JSON serialized merchant data

# 审核员权限缓存 (TTL: 15分钟)
key: "auditor_permissions:{user_id}"
value: JSON serialized permissions list

# 商家申请防重复提交锁 (TTL: 5秒)
key: "application_lock:{merchant_id}"
value: 1
```

### Invalidation Strategy
- 商家信息更新时主动失效缓存（Write-through）
- 审核状态变更时清空相关商家的缓存
- 使用 Redis Pub/Sub 通知多实例缓存失效（未来水平扩展）

---

## 4. Authentication & Authorization: JWT

### Decision
- **认证方式**: JWT (JSON Web Token)
- **授权模型**: RBAC (Role-Based Access Control)

### Rationale
1. **无状态**: JWT Token 自包含用户身份和权限，支持水平扩展
2. **双 Token 机制**: Access Token (15分钟) + Refresh Token (7天)，平衡安全性和用户体验
3. **细粒度权限**: 平台管理员（审核商家）vs 商家（查看自己的申请）

### Token Structure
```json
{
  "sub": "user_id",
  "role": "admin" | "merchant",
  "merchant_id": "optional_merchant_id",
  "permissions": ["审核商家", "查看商家"],
  "exp": 1609459200,
  "iat": 1609459200
}
```

### Security Measures
- Access Token 存储在内存（不持久化），15分钟自动过期
- Refresh Token 存储在 HttpOnly Cookie，防止 XSS 攻击
- Token 签名使用 RS256（非对称加密），私钥隔离存储
- 注销功能通过 Redis 黑名单实现（存储已注销的 Token JTI）

---

## 5. File Storage: Local Disk with Future S3 Compatibility

### Decision
- **初期**: 本地文件系统存储（`/var/data/uploads/`）
- **未来**: 兼容 S3 协议（MinIO/AWS S3），便于迁移

### Rationale
1. **简化部署**: 单服务器部署初期无需引入对象存储服务
2. **成本优化**: 本地磁盘存储无额外费用
3. **可迁移性**: 使用统一的文件服务接口，后续切换至 S3 无需修改业务代码

### File Organization
```
/var/data/uploads/
├── merchant_applications/
│   ├── {application_id}/
│   │   ├── business_license.jpg
│   │   ├── id_card_front.jpg
│   │   └── id_card_back.jpg
└── contracts/
    └── {merchant_id}/
        └── contract_{timestamp}.jpg
```

### Security Considerations
- 文件上传限制：类型（jpg/png/pdf）、大小（<10MB）
- 文件访问通过 API 签名 URL 控制权限（商家只能访问自己的文件）
- 定期清理未完成申请的临时文件（Celery 定时任务）

---

## 6. Asynchronous Task Queue: Celery

### Decision
使用 **Celery** + **Redis** 作为异步任务队列

### Rationale
1. **邮件发送**: 商家申请提交、审核结果通知（未来集成邮件服务）
2. **文件处理**: 图片压缩、OCR 识别营业执照信息（未来功能）
3. **定期任务**: 清理过期文件、生成审核报表

### Task Examples
```python
# 商家申请提交后异步任务
@celery.task
def send_application_notification(application_id):
    # 通知审核员有新申请（未来集成消息服务）
    pass

# 定期清理过期临时文件
@celery.task(schedule=crontab(hour=2, minute=0))
def cleanup_expired_files():
    # 删除30天前未完成申请的文件
    pass
```

---

## 7. Frontend: Ant Design Pro + Umi.js

### Decision
- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design Pro v6
- **路由**: Umi.js 约定式路由
- **构建工具**: Umi.js 内置 Webpack 配置

### Rationale
1. **企业级组件**: Ant Design Pro 提供开箱即用的中后台组件（表格、表单、权限）
2. **约定式路由**: Umi.js 基于目录结构自动生成路由，减少配置
3. **权限管理**: 内置 `access` 插件支持细粒度权限控制
4. **双前端共享**: Admin Frontend 和 Merchant Frontend 共享组件库和工具函数

### Project Structure
```
admin-frontend/src/
├── pages/               # 约定式路由页面
│   ├── merchants/index.tsx      → /merchants
│   ├── applications/audit.tsx   → /applications/audit
├── components/          # 共享业务组件
│   ├── MerchantCard/
│   ├── ApplicationForm/
│   └── AuditHistory/
├── services/            # API 请求封装
│   ├── merchant.ts
│   ├── application.ts
└── utils/               # 工具函数
    ├── request.ts       # Axios 封装 + JWT 拦截器
    └── auth.ts          # 认证工具函数
```

---

## 8. Testing Strategy

### Decision
- **单元测试**: pytest + pytest-asyncio (Backend), Jest (Frontend)
- **集成测试**: pytest + TestClient (FastAPI)
- **契约测试**: Schemathesis (基于 OpenAPI 自动生成)
- **E2E 测试**: Playwright (未来)

### Backend Testing
```python
# Unit Test Example
def test_create_application_service():
    application = create_application(data)
    assert application.status == ApplicationStatus.PENDING

# Integration Test Example
def test_submit_application_api(client, db_session):
    response = client.post("/api/v1/applications", json=data)
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"

# Contract Test (Schemathesis auto-generated)
schema.parametrize()(test_api_conforms_to_spec)
```

### Frontend Testing
```typescript
// Component Test Example
test('renders merchant list', async () => {
  render(<MerchantList />);
  await waitFor(() => expect(screen.getByText('商家列表')).toBeInTheDocument());
});

// Service Test Example
test('fetches merchant data', async () => {
  const data = await getMerchantById('123');
  expect(data.name).toBe('测试商家');
});
```

---

## 9. Deployment Architecture

### Decision
- **服务器**: 单机部署（Ubuntu 22.04 LTS）
- **Web 服务器**: Nginx (反向代理 + 静态文件服务)
- **应用服务器**: Uvicorn (FastAPI ASGI 服务器)
- **进程管理**: Systemd (生产环境)

### Deployment Topology
```
Internet → Nginx:443 (HTTPS)
  ├─→ /api/* → Uvicorn:8000 (FastAPI Backend)
  ├─→ /admin/* → Static Files (Admin Frontend)
  └─→ /merchant/* → Static Files (Merchant Frontend)

Backend → PostgreSQL:5432 (本地)
Backend → Redis:6379 (本地)
Backend → Celery Workers (本地)
```

### Nginx Configuration Highlights
- HTTPS 强制跳转（HTTP → HTTPS）
- Gzip 压缩静态资源
- API 请求代理到 Uvicorn
- 静态前端启用缓存策略（`Cache-Control: max-age=31536000` for versioned assets）

---

## 10. Development Workflow

### Decision
- **版本控制**: Git + Feature Branch 工作流
- **代码规范**: Pre-commit hooks (Black, isort, flake8, mypy, ESLint, Prettier)
- **CI/CD**: GitHub Actions (运行测试、Lint、构建 Docker 镜像)

### Pre-commit Configuration
```yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
  - repo: https://github.com/pre-commit/mirrors-eslint
    hooks:
      - id: eslint
        files: \.(ts|tsx|js|jsx)$
```

### Development Environment Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload

# Admin Frontend
cd admin-frontend
npm install
npm run dev

# Merchant Frontend
cd merchant-frontend
npm install
npm run dev
```

---

## 11. Security Best Practices

### Decision
遵循 OWASP Top 10 和 Constitution Security Requirements

### Implementation Checklist
- ✅ **SQL Injection**: 使用 SQLAlchemy 参数化查询，避免字符串拼接
- ✅ **XSS**: React 默认转义输出，Ant Design 组件安全性经过验证
- ✅ **CSRF**: SameSite Cookie + CSRF Token（未来 API 支持表单提交时启用）
- ✅ **认证**: JWT Token 短期过期 + Refresh Token 机制
- ✅ **授权**: RBAC 模型，每个 API 端点验证用户权限
- ✅ **文件上传**: 类型白名单、大小限制、文件内容验证（magic bytes）
- ✅ **日志脱敏**: 日志中屏蔽身份证号、电话号码（正则替换为 `***`）
- ✅ **依赖扫描**: 使用 `safety` (Python) 和 `npm audit` (Node.js) 检查漏洞

---

## 12. Performance Optimization

### Decision
遵循 Constitution 性能优先原则，API 响应 <200ms p95

### Optimization Strategies
1. **数据库优化**:
   - 索引策略（见第 2 节）
   - 分页查询（Limit + Offset，未来改用 Cursor Pagination）
   - N+1 查询问题：使用 SQLAlchemy `joinedload` 预加载关联数据

2. **缓存策略**:
   - Redis 缓存热点数据（商家信息、审核员权限）
   - HTTP 缓存头（静态资源 `Cache-Control`）

3. **异步处理**:
   - FastAPI 异步端点 (`async def`)
   - Celery 异步任务（邮件发送、文件处理）

4. **前端优化**:
   - 代码分割（Umi.js 自动按路由分割）
   - 图片懒加载（Ant Design `Image` 组件）
   - 虚拟滚动（长列表使用 `rc-virtual-list`）

---

## 13. Monitoring & Observability

### Decision
- **日志**: 结构化 JSON 日志（Python `logging` + `python-json-logger`）
- **指标**: Prometheus + Grafana（未来集成）
- **追踪**: Correlation ID 贯穿请求链路

### Logging Format
```json
{
  "timestamp": "2025-09-30T10:30:00Z",
  "level": "INFO",
  "correlation_id": "abc-123-def-456",
  "service": "merchant-api",
  "endpoint": "/api/v1/applications",
  "method": "POST",
  "user_id": "user-123",
  "merchant_id": "merchant-456",
  "message": "商家申请提交成功",
  "duration_ms": 45
}
```

---

## Summary

本研究文档涵盖商家入驻系统的所有关键技术决策，确保：
1. ✅ 符合 Constitution 所有核心原则（API-First、单体架构、TDD、性能优先）
2. ✅ 技术栈明确（FastAPI + React + PostgreSQL + Redis）
3. ✅ 架构决策有充分理由（性能、安全、可维护性）
4. ✅ 未来扩展性（S3 兼容、Prometheus 监控、水平扩展）

**下一步**: 执行 Phase 1 生成数据模型、API 契约和快速启动指南。