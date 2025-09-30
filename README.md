# grainAdminPro - 商家入驻管理系统

![Backend Status](https://img.shields.io/badge/Backend-80%25%20Complete-blue)
![Tests](https://img.shields.io/badge/Tests-21%2F21%20Passing-green)
![Coverage](https://img.shields.io/badge/Coverage-48%25-yellow)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688)

B2B2C 平台核心功能 - 商家入驻审核管理系统

## 📋 功能特性

### 已实现功能 (v1.0.0-backend)

- ✅ **用户认证与授权**
  - JWT 认证 (Access Token + Refresh Token)
  - Token 黑名单机制 (Redis)
  - 基于角色的权限控制 (Admin/Merchant/System)
  - 密码 bcrypt 加密

- ✅ **商家申请管理**
  - 商家入驻申请提交、查询、列表、统计
  - 审核流程 (待审核 → 审核中 → 通过/拒绝)
  - 审核意见和审核历史记录
  - 申请状态变更通知

- ✅ **商家信息管理**
  - 商家基本信息 CRUD
  - 商家状态管理 (正常/冻结/黑名单)
  - 商家列表查询和统计

- ✅ **文件上传管理**
  - 本地文件存储
  - 文件类型和大小限制 (10MB)
  - 营业执照、法人身份证、店铺照片上传
  - 安全路径处理

- ✅ **结构化日志与追踪**
  - 结构化 JSON 日志
  - Correlation ID 追踪
  - 按环境级别配置 (dev: DEBUG, prod: INFO)
  - 日志轮转 (TimedRotatingFileHandler)

- ✅ **性能优化**
  - Redis 缓存 (用户信息、商家信息)
  - 缓存失效机制 (创建/更新时自动失效)
  - 数据库查询优化 (索引、分页)
  - Celery 异步任务队列

- ✅ **可观测性**
  - 健康检查端点 (/health)
  - 完整的 OpenAPI 文档 (/docs, /redoc)
  - Correlation ID 中间件
  - CORS 跨域支持

- ✅ **部署配置**
  - Nginx 反向代理配置 (SSL/TLS, Gzip, 缓存)
  - Systemd 服务管理 (API, Celery Worker)
  - 环境变量配置 (.env.example)
  - 数据库迁移 (Alembic)

### 计划中功能 (v1.1.0-frontend)

- 📋 管理员前端 (React 18 + Ant Design Pro)
  - 商家申请审核页面
  - 商家管理页面
  - 数据统计看板

- 📋 商家前端 (React 18 + Ant Design Pro)
  - 入驻申请页面
  - 店铺信息管理
  - 合同管理页面

## 🛠️ 技术栈

### 后端

- **Web 框架**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0+ (异步)
- **数据库**: PostgreSQL 14+
- **缓存**: Redis 6+
- **任务队列**: Celery 5.3+ + Redis
- **数据验证**: Pydantic 2.5+
- **数据库迁移**: Alembic 1.13+
- **认证**: python-jose (JWT)
- **密码加密**: bcrypt
- **测试**: pytest + pytest-asyncio + httpx
- **代码质量**: Black, isort, flake8

### 前端 (计划中)

- **框架**: React 18
- **UI 组件库**: Ant Design Pro 5
- **路由**: Umi.js 4
- **状态管理**: dva
- **HTTP 客户端**: umi-request

### 部署

- **Web 服务器**: Nginx (反向代理)
- **进程管理**: Systemd
- **WSGI 服务器**: Uvicorn (多进程)

## 📁 项目结构

```
grainAdminPro/
├── backend/                 # 后端 API (FastAPI + SQLAlchemy + PostgreSQL)
│   ├── src/
│   │   ├── api/            # API 路由
│   │   │   └── v1/
│   │   │       ├── applications.py   # 商家申请 API (13 个端点)
│   │   │       ├── merchants.py      # 商家管理 API (7 个端点)
│   │   │       ├── auth.py          # 认证 API (4 个端点)
│   │   │       └── upload.py        # 文件上传 API (1 个端点)
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py           # 应用配置
│   │   │   ├── database.py         # 数据库连接
│   │   │   ├── redis.py            # Redis 连接
│   │   │   ├── celery_app.py       # Celery 配置
│   │   │   ├── security.py         # JWT 认证
│   │   │   └── logging.py          # 结构化日志
│   │   ├── models/         # 数据库模型
│   │   │   ├── user.py             # 用户模型
│   │   │   ├── merchant.py         # 商家模型
│   │   │   ├── application.py      # 申请模型
│   │   │   ├── audit.py            # 审核记录模型
│   │   │   └── contract.py         # 合同模型 (预留)
│   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── merchant.py
│   │   │   ├── application.py
│   │   │   ├── audit.py
│   │   │   └── common.py
│   │   ├── services/       # 业务逻辑
│   │   │   ├── application_service.py
│   │   │   ├── merchant_service.py
│   │   │   ├── audit_service.py
│   │   │   └── user_service.py
│   │   ├── middleware/     # 中间件
│   │   │   └── correlation_id.py   # Correlation ID 追踪
│   │   ├── utils/          # 工具函数
│   │   │   ├── pagination.py       # 分页工具
│   │   │   └── file_storage.py     # 文件存储
│   │   └── main.py         # FastAPI 入口
│   ├── tests/              # 测试
│   │   ├── conftest.py             # pytest fixtures
│   │   ├── test_*.py               # 各模块测试 (21 个测试)
│   │   └── test_backend_integration.py  # 集成测试
│   ├── alembic/            # 数据库迁移
│   │   ├── env.py
│   │   └── versions/
│   ├── logs/               # 日志目录
│   ├── uploads/            # 本地文件上传目录
│   ├── scripts/            # 工具脚本
│   │   └── check_prerequisites.sh  # 环境检查脚本
│   ├── requirements.txt    # 生产依赖
│   ├── requirements-dev.txt # 开发依赖
│   ├── .env.example        # 环境变量示例
│   └── pyproject.toml      # 项目配置
│
├── admin-frontend/         # 管理员前端 (React 18 + Ant Design Pro)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Application/        # 商家申请审核页面
│   │   │   └── Merchant/           # 商家管理页面
│   │   ├── services/               # API 客户端
│   │   ├── models/                 # 数据模型
│   │   └── app.tsx
│   ├── .umirc.ts
│   └── package.json
│
├── merchant-frontend/      # 商家前端 (React 18 + Ant Design Pro)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Application/        # 入驻申请页面
│   │   │   ├── MerchantInfo/       # 店铺信息管理
│   │   │   └── Contract/           # 合同管理页面
│   │   ├── services/               # API 客户端
│   │   ├── models/                 # 数据模型
│   │   └── app.tsx
│   ├── .umirc.ts
│   └── package.json
│
├── deployment/             # 部署配置
│   ├── nginx.conf                  # Nginx 配置
│   ├── grainadmin-api.service      # API Systemd 服务
│   └── grainadmin-celery.service   # Celery Systemd 服务
│
└── specs/                  # 功能规范文档
    └── 001-b2b2c/
        ├── spec.md         # 需求规范
        ├── plan.md         # 实施计划
        ├── data-model.md   # 数据模型
        ├── tasks.md        # 任务列表 (60 个任务)
        └── SETUP.md        # 环境搭建指南
```

## 🚀 快速启动

### 1. 克隆项目

```bash
git clone <repository-url>
cd grainAdminPro
```

### 2. 后端安装

```bash
cd backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 配置环境变量
cp .env.example .env
vim .env  # 修改数据库、Redis 配置

# 初始化数据库
alembic upgrade head

# 运行开发服务器
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

访问:
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 3. 前端安装 (计划中)

```bash
# 管理员前端
cd admin-frontend
npm install
npm run start  # http://localhost:8001

# 商家前端
cd merchant-frontend
npm install
npm run start  # http://localhost:8002
```

## 📝 API 端点

### 认证 API (`/api/v1/auth`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/auth/register` | 用户注册 | ❌ |
| POST | `/auth/login` | 用户登录 | ❌ |
| POST | `/auth/refresh` | 刷新 Token | ✅ |
| POST | `/auth/logout` | 用户登出 | ✅ |

### 商家申请 API (`/api/v1/applications`)

| 方法 | 端点 | 描述 | 认证 | 角色 |
|------|------|------|------|------|
| POST | `/applications` | 提交商家申请 | ✅ | Merchant |
| GET | `/applications/{id}` | 查询申请详情 | ✅ | Admin/Merchant |
| GET | `/applications` | 申请列表 (分页) | ✅ | Admin |
| GET | `/applications/my` | 我的申请列表 | ✅ | Merchant |
| GET | `/applications/stats` | 申请统计数据 | ✅ | Admin |
| POST | `/applications/{id}/submit` | 提交审核 | ✅ | Merchant |
| POST | `/applications/{id}/approve` | 审核通过 | ✅ | Admin |
| POST | `/applications/{id}/reject` | 审核拒绝 | ✅ | Admin |
| POST | `/applications/{id}/start-review` | 开始审核 | ✅ | Admin |
| POST | `/applications/{id}/request-info` | 请求补充资料 | ✅ | Admin |
| POST | `/applications/{id}/supplement` | 提交补充资料 | ✅ | Merchant |
| POST | `/applications/{id}/cancel` | 取消申请 | ✅ | Merchant |
| GET | `/applications/{id}/audits` | 审核历史 | ✅ | Admin/Merchant |

### 商家管理 API (`/api/v1/merchants`)

| 方法 | 端点 | 描述 | 认证 | 角色 |
|------|------|------|------|------|
| GET | `/merchants/{id}` | 查询商家详情 | ✅ | Admin/Merchant |
| GET | `/merchants` | 商家列表 (分页) | ✅ | Admin |
| PUT | `/merchants/{id}` | 更新商家信息 | ✅ | Admin/Merchant |
| GET | `/merchants/stats` | 商家统计数据 | ✅ | Admin |
| POST | `/merchants/{id}/freeze` | 冻结商家 | ✅ | Admin |
| POST | `/merchants/{id}/unfreeze` | 解冻商家 | ✅ | Admin |
| POST | `/merchants/{id}/blacklist` | 加入黑名单 | ✅ | Admin |

### 文件上传 API (`/api/v1/upload`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/upload` | 上传文件 | ✅ |

## 🧪 测试

### 运行所有测试

```bash
cd backend
pytest
```

### 测试覆盖率

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### 测试统计

- **总测试数**: 21
- **通过率**: 100%
- **代码覆盖率**: 48%
- **测试类型**: 单元测试 + 集成测试

### 测试覆盖的模块

- ✅ 用户认证和授权 (auth.py)
- ✅ 商家申请管理 (applications.py)
- ✅ 商家信息管理 (merchants.py)
- ✅ 文件上传 (upload.py)
- ✅ 健康检查和文档
- ✅ CORS 和中间件
- ✅ Correlation ID 追踪

## 🔧 配置说明

### 环境变量 (`.env`)

```bash
# 应用配置
APP_NAME=grainadmin
APP_VERSION=1.0.0
APP_ENV=development  # development | production

# 服务器配置
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/grainadmin

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # 可选

# JWT 配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 文件上传配置
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 日志配置
LOG_LEVEL=DEBUG  # DEBUG | INFO | WARNING | ERROR
LOG_DIR=logs
```

### 数据库迁移

```bash
# 自动生成迁移文件
alembic revision --autogenerate -m "描述迁移内容"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

## 🚀 生产部署

### 部署架构

```
[浏览器] → [Nginx:443] → [Uvicorn:8000] → [PostgreSQL:5432]
                       ↓                    ↑
                  [Celery Worker] → [Redis:6379]
```

### 快速部署步骤

1. **安装依赖**

```bash
# 创建服务用户
sudo useradd -r -s /bin/false grainadmin

# 创建目录
sudo mkdir -p /opt/grainadmin/backend
sudo mkdir -p /var/data/grainadmin/uploads
sudo chown -R grainadmin:grainadmin /opt/grainadmin
```

2. **部署代码**

```bash
# 复制代码
sudo -u grainadmin cp -r backend/* /opt/grainadmin/backend/

# 安装 Python 依赖
sudo -u grainadmin python3 -m venv /opt/grainadmin/backend/venv
sudo -u grainadmin /opt/grainadmin/backend/venv/bin/pip install -r /opt/grainadmin/backend/requirements.txt

# 配置环境变量
sudo cp backend/.env.example /opt/grainadmin/backend/.env.production
sudo vim /opt/grainadmin/backend/.env.production
sudo chown grainadmin:grainadmin /opt/grainadmin/backend/.env.production
sudo chmod 600 /opt/grainadmin/backend/.env.production
```

3. **应用数据库迁移**

```bash
sudo -u grainadmin /opt/grainadmin/backend/venv/bin/alembic upgrade head
```

4. **配置 Systemd 服务**

```bash
# 安装 API 服务
sudo cp deployment/grainadmin-api.service /etc/systemd/system/
sudo systemctl enable grainadmin-api
sudo systemctl start grainadmin-api

# 安装 Celery 服务
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown -R grainadmin:grainadmin /var/run/celery /var/log/celery
sudo cp deployment/grainadmin-celery.service /etc/systemd/system/
sudo systemctl enable grainadmin-celery
sudo systemctl start grainadmin-celery
```

5. **配置 Nginx**

```bash
# 安装 Nginx 配置
sudo cp deployment/nginx.conf /etc/nginx/sites-available/grainadmin
sudo ln -s /etc/nginx/sites-available/grainadmin /etc/nginx/sites-enabled/

# 配置 SSL 证书 (Let's Encrypt)
sudo certbot --nginx -d example.com -d www.example.com

# 重载 Nginx
sudo nginx -t
sudo systemctl reload nginx
```

6. **验证部署**

```bash
# 检查服务状态
sudo systemctl status grainadmin-api
sudo systemctl status grainadmin-celery

# 查看日志
sudo journalctl -u grainadmin-api -f
sudo journalctl -u grainadmin-celery -f

# 测试 API
curl https://example.com/health
```

详细部署说明请参考:
- [Nginx 配置说明](deployment/nginx.conf)
- [Systemd 服务配置](deployment/grainadmin-api.service)

## 💻 开发指南

### 代码规范

```bash
# 格式化代码
black src/ tests/

# 排序 imports
isort src/ tests/

# 代码检查
flake8 src/ tests/
```

### 开发工作流 (TDD)

1. **编写测试**: 在 `tests/` 目录下创建测试文件
2. **运行测试**: `pytest` (测试应该失败)
3. **编写代码**: 实现功能使测试通过
4. **重构**: 优化代码保持测试通过
5. **提交代码**: `git commit -m "描述"`

### Git 提交规范

```bash
git commit -m "type(scope): subject"

# 类型 (type):
# - feat: 新功能
# - fix: 修复 bug
# - docs: 文档更新
# - style: 代码格式调整
# - refactor: 代码重构
# - test: 测试相关
# - chore: 构建/工具相关

# 示例:
git commit -m "feat(auth): 实现 JWT 认证"
git commit -m "fix(applications): 修复申请状态更新 bug"
git commit -m "docs(readme): 更新部署指南"
```

### 添加新的 API 端点

1. 在 `src/models/` 创建/更新数据库模型
2. 在 `src/schemas/` 创建 Pydantic schema
3. 在 `src/services/` 实现业务逻辑
4. 在 `src/api/v1/` 创建 API 路由
5. 在 `tests/` 编写测试
6. 生成数据库迁移: `alembic revision --autogenerate -m "描述"`

## 🔗 相关文档

- [环境搭建指南](specs/001-b2b2c/SETUP.md) - 详细的本地开发环境配置
- [功能需求规范](specs/001-b2b2c/spec.md) - 完整的功能需求文档
- [数据模型设计](specs/001-b2b2c/data-model.md) - 数据库表结构和关系
- [实施任务列表](specs/001-b2b2c/tasks.md) - 60 个详细任务分解

## 🤝 贡献指南

我们欢迎任何形式的贡献!

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码审查检查清单

- [ ] 代码通过所有测试 (`pytest`)
- [ ] 代码符合格式规范 (`black`, `isort`, `flake8`)
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息遵循规范

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

- 项目维护者: Griffith
- 问题反馈: [GitHub Issues](https://github.com/yourorg/grainAdminPro/issues)

## 📊 项目状态

### 当前版本: v1.0.0-backend (2025-09-30)

**项目完成度**: 83% (50/60 任务)

### v1.0.0 - 后端完成 ✅

- [x] 项目初始化和环境配置
- [x] 数据库模型和迁移
- [x] API 端点实现 (25 个端点)
- [x] JWT 认证和授权
- [x] 文件上传功能
- [x] Redis 缓存优化
- [x] Celery 异步任务
- [x] 结构化日志和追踪
- [x] 单元测试和集成测试 (21 个测试)
- [x] 部署配置 (Nginx, Systemd)

### v1.1.0 - 前端开发 (计划中)

- [ ] 管理员前端 (React + Ant Design Pro)
  - [ ] 商家申请审核页面
  - [ ] 商家管理页面
  - [ ] 数据统计看板
- [ ] 商家前端 (React + Ant Design Pro)
  - [ ] 入驻申请页面
  - [ ] 店铺信息管理
  - [ ] 合同管理页面

### v2.0.0 - 高级功能 (未来)

- [ ] 实时通知 (WebSocket)
- [ ] 数据导出 (Excel)
- [ ] 高级报表和分析
- [ ] 多语言支持
- [ ] 移动端适配

---

**最后更新**: 2025-09-30
**版本**: 1.0.0-backend
**分支**: 001-b2b2c