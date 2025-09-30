# Environment Setup Guide

**Feature**: 001-b2b2c | **Date**: 2025-09-30

本文档提供商家入驻管理系统的完整环境配置指南，从零开始搭建开发环境。

---

## Prerequisites

确保已安装以下软件：

- **Python 3.11+**: `python --version`
- **Node.js 18+**: `node --version`
- **PostgreSQL 14+**: `psql --version`
- **Redis 6+**: `redis-cli --version`
- **Git**: `git --version`

---

## Step 1: Clone Repository

```bash
cd /path/to/your/workspace
git clone <repository-url> grainAdminPro
cd grainAdminPro
git checkout 001-b2b2c
```

---

## Step 2: Database Setup

### 2.1 Install PostgreSQL

**macOS (Homebrew)**:
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql-14 postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows**:
下载安装器：https://www.postgresql.org/download/windows/

### 2.2 Use Existing Superuser (推荐 - 适用于已有超级用户的情况)

如果你已经创建了 PostgreSQL 超级用户（如 padmin），直接使用即可：

```bash
# 进入 PostgreSQL 命令行（使用你的超级用户）
psql -U padmin -d postgres

# 创建项目数据库
CREATE DATABASE grainadmin_dev;

# 退出
\q
```

### 2.3 Verify Database Connection

```bash
psql -h localhost -U padmin -d grainadmin_dev -c "SELECT 1;"
# 输入你的超级用户密码
# 期望输出: 1 row
```

### 2.4 Alternative: Create Dedicated User (备选方案)

如果想创建专用的项目用户（更安全但配置更复杂）：

```bash
# 进入 PostgreSQL 命令行
sudo -u postgres psql

# 在 psql 中执行以下命令
CREATE USER grainadmin_user WITH PASSWORD 'dev_password_123';
CREATE DATABASE grainadmin_dev OWNER grainadmin_user;
GRANT ALL PRIVILEGES ON DATABASE grainadmin_dev TO grainadmin_user;
\q
```

然后在 `.env` 中使用：
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/grainadmin_dev
```

---

## Step 3: Redis Setup

### 3.1 Install Redis

**macOS (Homebrew)**:
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Windows**:
使用 WSL 或下载 Windows 版本：https://redis.io/docs/getting-started/installation/install-redis-on-windows/

### 3.2 Verify Redis Connection

```bash
redis-cli ping
# 期望输出: PONG
```

---

## Step 4: Backend Configuration

### 4.1 Copy Environment Template

```bash
cd backend
cp .env.example .env
```

### 4.2 Review and Customize .env

打开 `backend/.env` 文件，检查以下关键配置：

**数据库连接** (使用你的实际超级用户凭据):
```env
DATABASE_URL=postgresql://padmin:Qwe!1234@localhost:5432/grainadmin_dev
```

**Redis 连接** (本地开发默认配置):
```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

**JWT 密钥** (开发环境可以保持默认，生产环境必须修改):
```env
JWT_SECRET_KEY=dev-secret-key-change-in-production-use-at-least-32-chars
```

**文件上传目录** (开发环境使用相对路径):
```env
UPLOAD_DIR=./uploads
```

**CORS 允许的前端域名**:
```env
CORS_ORIGINS=http://localhost:8001,http://localhost:8002
```

### 4.3 Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 4.4 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4.5 Initialize Database Schema

```bash
# 初始化 Alembic (如果还没有)
alembic init alembic

# 运行数据库迁移
alembic upgrade head
```

### 4.6 Create Upload Directory

```bash
mkdir -p uploads/merchant_applications
mkdir -p uploads/contracts
chmod 755 uploads
```

---

## Step 5: Admin Frontend Configuration

### 5.1 Install Dependencies

```bash
cd ../admin-frontend
npm install
```

### 5.2 Create Environment File

```bash
cat > .env << EOF
PORT=8001
API_BASE_URL=http://localhost:8000
UMI_ENV=development
EOF
```

### 5.3 Configure API Proxy (if needed)

编辑 `admin-frontend/.umirc.ts`，确保 proxy 配置正确：

```typescript
export default defineConfig({
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
});
```

---

## Step 6: Merchant Frontend Configuration

### 6.1 Install Dependencies

```bash
cd ../merchant-frontend
npm install
```

### 6.2 Create Environment File

```bash
cat > .env << EOF
PORT=8002
API_BASE_URL=http://localhost:8000
UMI_ENV=development
EOF
```

---

## Step 7: Start Services

### 7.1 Start Backend API

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

验证 API 运行：
```bash
curl http://localhost:8000/health
# 期望输出: {"status":"ok"}
```

访问 API 文档：http://localhost:8000/docs

### 7.2 Start Celery Worker (Optional)

在新终端窗口：
```bash
cd backend
source venv/bin/activate
celery -A src.celery_app worker -l info
```

### 7.3 Start Admin Frontend

在新终端窗口：
```bash
cd admin-frontend
npm run dev
```

访问：http://localhost:8001

### 7.4 Start Merchant Frontend

在新终端窗口：
```bash
cd merchant-frontend
npm run dev
```

访问：http://localhost:8002

---

## Step 8: Verification

### 8.1 Check All Services

运行以下命令验证所有服务正常：

```bash
# Backend API
curl http://localhost:8000/health

# PostgreSQL
psql -h localhost -U padmin -d grainadmin_dev -c "SELECT version();"

# Redis
redis-cli ping

# Admin Frontend
curl http://localhost:8001

# Merchant Frontend
curl http://localhost:8002
```

### 8.2 Run Tests

```bash
cd backend
pytest tests/ -v
```

---

## Common Issues & Troubleshooting

### Issue 1: PostgreSQL Connection Failed

**Symptom**:
```
psycopg2.OperationalError: could not connect to server
```

**Solutions**:
1. 检查 PostgreSQL 是否运行：`pg_isready`
2. 检查端口：`sudo lsof -i :5432`
3. 检查 `pg_hba.conf` 允许本地连接
4. 重启 PostgreSQL：`brew services restart postgresql@14`

### Issue 2: Redis Connection Refused

**Symptom**:
```
redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379
```

**Solutions**:
1. 启动 Redis：`redis-server` 或 `brew services start redis`
2. 检查端口：`sudo lsof -i :6379`
3. 测试连接：`redis-cli ping`

### Issue 3: Permission Denied on Upload Directory

**Symptom**:
```
PermissionError: [Errno 13] Permission denied: './uploads'
```

**Solutions**:
```bash
mkdir -p backend/uploads
chmod 755 backend/uploads
```

### Issue 4: Frontend Cannot Connect to API

**Symptom**:
```
Network Error or CORS Error in browser console
```

**Solutions**:
1. 检查后端 API 是否运行：`curl http://localhost:8000/health`
2. 检查 `.env` 中的 `CORS_ORIGINS` 包含前端 URL
3. 检查前端 `.env` 中的 `API_BASE_URL` 正确
4. 清除浏览器缓存并重新加载

### Issue 5: Alembic Migration Failed

**Symptom**:
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solutions**:
```bash
# 查看当前迁移状态
alembic current

# 回滚到基础版本
alembic downgrade base

# 重新运行迁移
alembic upgrade head
```

### Issue 6: Python Module Not Found

**Symptom**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions**:
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

---

## Environment Variables Reference

详细的环境变量说明见 `backend/.env.example` 文件。

**必须配置的变量** (Minimum Required):
- `DATABASE_URL` - PostgreSQL 连接字符串
- `REDIS_URL` - Redis 连接字符串
- `JWT_SECRET_KEY` - JWT Token 签名密钥

**推荐配置的变量**:
- `CORS_ORIGINS` - 允许的前端域名
- `UPLOAD_DIR` - 文件上传目录

---

## Security Checklist for Production

部署到生产环境前，务必完成以下安全检查：

- [ ] 修改 `JWT_SECRET_KEY` 为强密码（至少32字符）
- [ ] 使用 RS256 算法并生成 RSA 密钥对
- [ ] 修改数据库密码为强密码（至少16字符）
- [ ] 设置 `DEBUG=False`
- [ ] 配置 HTTPS（Nginx + Let's Encrypt）
- [ ] 限制 `CORS_ORIGINS` 为实际域名
- [ ] 启用防火墙，仅开放必要端口（80, 443）
- [ ] 配置数据库连接池大小
- [ ] 启用 Sentry 错误追踪
- [ ] 配置日志轮转和备份
- [ ] 运行安全扫描：`safety check` 和 `npm audit`

---

## Next Steps

环境配置完成后，继续执行：

1. **Run Quickstart**: 参考 `specs/001-b2b2c/quickstart.md` 测试核心功能
2. **Execute Tasks**: 按照 `specs/001-b2b2c/tasks.md` 开始实施开发任务
3. **Read Documentation**: 查看 `specs/001-b2b2c/research.md` 了解技术决策

---

**Last Updated**: 2025-09-30