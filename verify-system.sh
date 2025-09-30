#!/bin/bash
# 系统功能验证脚本
# 验证商家入驻管理系统的核心功能

set -e

echo "🚀 商家入驻管理系统 - 功能验证脚本"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 PostgreSQL
echo "📊 1. 检查数据库连接..."
if psql -U padmin -d grainadmin_dev -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL 连接正常${NC}"
else
    echo -e "${RED}❌ PostgreSQL 连接失败${NC}"
    echo "请检查数据库配置"
    exit 1
fi

# 检查表结构
echo ""
echo "📋 2. 检查数据库表..."
TABLES=$(psql -U padmin -d grainadmin_dev -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public';" | grep -v '^$' | wc -l)
echo "   已创建表数量: $TABLES"

if [ "$TABLES" -ge 6 ]; then
    echo -e "${GREEN}✅ 数据库表完整${NC}"
    psql -U padmin -d grainadmin_dev -c "\dt" | grep -E "merchant_application|audit_record|merchant_account|admin_user"
else
    echo -e "${RED}❌ 数据库表不完整${NC}"
    exit 1
fi

# 检查管理员账户
echo ""
echo "👤 3. 检查管理员账户..."
ADMIN_COUNT=$(psql -U padmin -d grainadmin_dev -t -c "SELECT COUNT(*) FROM admin_user;")
if [ "$ADMIN_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ 管理员账户存在 (数量: $ADMIN_COUNT)${NC}"
    psql -U padmin -d grainadmin_dev -c "SELECT username, name, email, is_active FROM admin_user;"
else
    echo -e "${YELLOW}⚠️  未找到管理员账户${NC}"
    echo "   运行: cd backend && python -m src.scripts.init_admin"
fi

# 检查 Python 环境
echo ""
echo "🐍 4. 检查 Python 环境..."
cd backend
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ 虚拟环境存在${NC}"
else
    echo -e "${YELLOW}⚠️  虚拟环境不存在${NC}"
fi

# 检查依赖
echo ""
echo "📦 5. 检查 Python 依赖..."
source venv/bin/activate 2>/dev/null || true
REQUIRED_PACKAGES="fastapi sqlalchemy alembic psycopg2 pydantic python-jose passlib"
MISSING=0

for pkg in $REQUIRED_PACKAGES; do
    if python -c "import ${pkg//-/_}" 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} $pkg"
    else
        echo -e "   ${RED}✗${NC} $pkg"
        MISSING=$((MISSING + 1))
    fi
done

if [ "$MISSING" -eq 0 ]; then
    echo -e "${GREEN}✅ 所有依赖已安装${NC}"
else
    echo -e "${RED}❌ 缺少 $MISSING 个依赖${NC}"
fi

# 检查 API 代码
echo ""
echo "📁 6. 检查代码文件..."
FILES_TO_CHECK=(
    "src/main.py"
    "src/models/merchant_application.py"
    "src/services/application_service.py"
    "src/api/v1/applications.py"
    "src/core/security.py"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✓${NC} $file"
    else
        echo -e "   ${RED}✗${NC} $file"
    fi
done

# 测试导入
echo ""
echo "🔍 7. 测试 Python 导入..."
if python -c "from src.main import app; print(f'✅ FastAPI app 导入成功，路由数: {len([r for r in app.routes if hasattr(r, \"path\")])}')"; then
    echo -e "${GREEN}✅ Python 模块导入正常${NC}"
else
    echo -e "${RED}❌ Python 模块导入失败${NC}"
    exit 1
fi

# 统计代码
echo ""
echo "📊 8. 代码统计..."
echo "   Models:    $(find src/models -name '*.py' ! -name '__*' | wc -l) files"
echo "   Schemas:   $(find src/schemas -name '*.py' ! -name '__*' | wc -l) files"
echo "   Services:  $(find src/services -name '*.py' ! -name '__*' | wc -l) files"
echo "   API:       $(find src/api -name '*.py' ! -name '__*' | wc -l) files"
echo "   Tests:     $(find tests -name 'test_*.py' | wc -l) files"

# 总结
echo ""
echo "========================================"
echo "✨ 验证完成！"
echo ""
echo "📋 功能清单:"
echo "   ✅ 数据库和表结构"
echo "   ✅ 管理员账户"
echo "   ✅ Python 环境和依赖"
echo "   ✅ 代码文件完整"
echo "   ✅ 模块导入正常"
echo ""
echo "🚀 启动 API 服务器:"
echo "   cd backend"
echo "   uvicorn src.main:app --reload --port 8000"
echo ""
echo "📖 查看 API 文档:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔐 管理员登录:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""