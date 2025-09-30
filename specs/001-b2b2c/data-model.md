# Data Model: 商家入驻管理系统

**Feature**: 001-b2b2c | **Date**: 2025-09-30
**Database**: PostgreSQL 14+ | **ORM**: SQLAlchemy 2.0

---

## Entity Relationship Diagram

```
┌────────────────────────┐
│  MerchantApplication   │
│────────────────────────│
│ id (PK)                │
│ business_name          │
│ unified_social_credit  │◄──┐
│ legal_person_name      │   │
│ legal_person_id_number │   │
│ contact_name           │   │
│ contact_phone          │   │
│ contact_email          │   │
│ business_categories    │   │  1:N
│ status (ENUM)          │   │
│ submitted_at           │   │
│ created_at             │   │
│ updated_at             │   │
└────────────────────────┘   │
                             │
                             │
┌────────────────────────┐   │
│     AuditRecord        │───┘
│────────────────────────│
│ id (PK)                │
│ application_id (FK)    │
│ auditor_id (FK)        │
│ auditor_name           │
│ action (ENUM)          │
│ result (ENUM)          │
│ comment                │
│ created_at             │
└────────────────────────┘


┌────────────────────────┐       ┌────────────────────────┐
│   MerchantAccount      │◄──────│   ContractFile         │
│────────────────────────│  1:N  │────────────────────────│
│ id (PK)                │       │ id (PK)                │
│ merchant_id (Unique)   │       │ merchant_id (FK)       │
│ username               │       │ file_path              │
│ password_hash          │       │ file_size              │
│ level (ENUM)           │       │ file_type              │
│ status (ENUM)          │       │ upload_by              │
│ application_id (FK)    │       │ uploaded_at            │
│ created_at             │       │ created_at             │
│ updated_at             │       └────────────────────────┘
└────────────────────────┘
       ▲
       │ 1:N
       │
┌────────────────────────┐
│  QualificationFile     │
│────────────────────────│
│ id (PK)                │
│ application_id (FK)    │
│ merchant_id (FK)       │
│ file_type (ENUM)       │
│ file_path              │
│ file_size              │
│ audit_status (ENUM)    │
│ uploaded_at            │
│ created_at             │
└────────────────────────┘
```

---

## 1. MerchantApplication (商家申请)

### Purpose
存储商家入驻申请的核心信息，包括企业信息、法人信息、联系方式和申请状态。

### Fields

| Field                   | Type         | Constraints           | Description                              |
|-------------------------|--------------|-----------------------|------------------------------------------|
| `id`                    | UUID         | PRIMARY KEY           | 申请唯一标识                             |
| `business_name`         | VARCHAR(200) | NOT NULL              | 企业名称                                 |
| `unified_social_credit` | VARCHAR(18)  | NOT NULL, UNIQUE      | 统一社会信用代码（营业执照号）           |
| `legal_person_name`     | VARCHAR(100) | NOT NULL              | 法人姓名                                 |
| `legal_person_id_number`| VARCHAR(18)  | NOT NULL, ENCRYPTED   | 法人身份证号（加密存储）                 |
| `contact_name`          | VARCHAR(100) | NOT NULL              | 联系人姓名                               |
| `contact_phone`         | VARCHAR(20)  | NOT NULL, ENCRYPTED   | 联系电话（加密存储）                     |
| `contact_email`         | VARCHAR(255) | NOT NULL              | 联系邮箱                                 |
| `business_categories`   | JSONB        | NOT NULL              | 经营类目（数组，如 ["食品", "服装"]）   |
| `status`                | ENUM         | NOT NULL, DEFAULT='PENDING' | 申请状态（见 ApplicationStatus）       |
| `submitted_at`          | TIMESTAMP    | NULL                  | 提交时间（从草稿状态提交时记录）         |
| `created_at`            | TIMESTAMP    | NOT NULL, DEFAULT=NOW | 创建时间                                 |
| `updated_at`            | TIMESTAMP    | NOT NULL, DEFAULT=NOW | 更新时间                                 |

### Enums

#### ApplicationStatus
```python
class ApplicationStatus(str, Enum):
    DRAFT = "draft"                    # 草稿（商家填写中）
    PENDING = "pending"                # 待审核（已提交）
    UNDER_REVIEW = "under_review"      # 审核中（审核员正在处理）
    REQUIRE_SUPPLEMENT = "require_supplement"  # 要求补充材料
    APPROVED = "approved"              # 审核通过
    REJECTED = "rejected"              # 审核拒绝
```

### Validation Rules
- `unified_social_credit`: 18位统一社会信用代码格式验证（正则：`^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$`）
- `legal_person_id_number`: 18位身份证号格式验证（正则：`^\d{17}[\dXx]$`）
- `contact_phone`: 11位手机号或固定电话格式验证
- `contact_email`: 标准邮箱格式验证
- `business_categories`: 非空数组，至少包含 1 个类目

### State Transitions
```
DRAFT → PENDING (商家提交申请)
PENDING → UNDER_REVIEW (审核员开始审核)
UNDER_REVIEW → APPROVED (审核通过)
UNDER_REVIEW → REJECTED (审核拒绝)
UNDER_REVIEW → REQUIRE_SUPPLEMENT (要求补充材料)
REQUIRE_SUPPLEMENT → PENDING (商家重新提交)
```

### Indexes
```sql
CREATE INDEX idx_merchant_application_status ON merchant_application(status, created_at);
CREATE INDEX idx_merchant_application_submitted_at ON merchant_application(submitted_at DESC);
CREATE INDEX idx_merchant_application_credit_code ON merchant_application(unified_social_credit);
CREATE INDEX idx_merchant_application_business_name ON merchant_application USING gin(to_tsvector('jiebacfg', business_name));
```

---

## 2. AuditRecord (审核记录)

### Purpose
记录商家申请的每一次审核操作，确保审核过程可追溯（满足 FR-009）。

### Fields

| Field            | Type         | Constraints           | Description                                |
|------------------|--------------|-----------------------|--------------------------------------------|
| `id`             | UUID         | PRIMARY KEY           | 审核记录唯一标识                           |
| `application_id` | UUID         | NOT NULL, FK          | 关联商家申请 ID                            |
| `auditor_id`     | UUID         | NOT NULL, FK          | 审核员用户 ID（关联用户表，本 feature 未实现）|
| `auditor_name`   | VARCHAR(100) | NOT NULL              | 审核员姓名（冗余存储，便于历史查询）       |
| `action`         | ENUM         | NOT NULL              | 审核动作（见 AuditAction）                 |
| `result`         | ENUM         | NOT NULL              | 审核结果（见 AuditResult）                 |
| `comment`        | TEXT         | NULL                  | 审核意见/备注                              |
| `created_at`     | TIMESTAMP    | NOT NULL, DEFAULT=NOW | 审核时间                                   |

### Enums

#### AuditAction
```python
class AuditAction(str, Enum):
    START_REVIEW = "start_review"            # 开始审核
    APPROVE = "approve"                      # 审核通过
    REJECT = "reject"                        # 审核拒绝
    REQUEST_SUPPLEMENT = "request_supplement"  # 要求补充材料
```

#### AuditResult
```python
class AuditResult(str, Enum):
    APPROVED = "approved"              # 通过
    REJECTED = "rejected"              # 拒绝
    PENDING_SUPPLEMENT = "pending_supplement"  # 待补充材料
    IN_PROGRESS = "in_progress"        # 审核中（开始审核时）
```

### Business Rules
- 每次状态变更必须创建审核记录（通过数据库触发器或应用层强制）
- `comment` 字段在 `REJECT` 和 `REQUEST_SUPPLEMENT` 操作时为必填
- 审核记录不可修改或删除（仅支持插入）

### Indexes
```sql
CREATE INDEX idx_audit_record_application_id ON audit_record(application_id, created_at DESC);
CREATE INDEX idx_audit_record_auditor_id ON audit_record(auditor_id);
CREATE INDEX idx_audit_record_created_at ON audit_record(created_at DESC);
```

---

## 3. MerchantAccount (商家账户)

### Purpose
存储审核通过后自动创建的商家登录账户，包含登录凭证、等级和状态（满足 FR-004, FR-005, FR-008）。

### Fields

| Field            | Type         | Constraints           | Description                                    |
|------------------|--------------|-----------------------|------------------------------------------------|
| `id`             | UUID         | PRIMARY KEY           | 商家账户唯一标识                               |
| `merchant_id`    | VARCHAR(20)  | NOT NULL, UNIQUE      | 商家编号（如 `M20250930001`）                  |
| `username`       | VARCHAR(50)  | NOT NULL, UNIQUE      | 登录用户名（默认使用联系人电话或邮箱）         |
| `password_hash`  | VARCHAR(255) | NOT NULL              | 密码哈希（使用 bcrypt）                        |
| `level`          | ENUM         | NOT NULL, DEFAULT='NORMAL' | 商家等级（见 MerchantLevel）                |
| `status`         | ENUM         | NOT NULL, DEFAULT='ACTIVE' | 账户状态（见 MerchantStatus）                |
| `application_id` | UUID         | NOT NULL, FK, UNIQUE  | 关联的入驻申请 ID（一个申请对应一个账户）      |
| `created_at`     | TIMESTAMP    | NOT NULL, DEFAULT=NOW | 账户创建时间                                   |
| `updated_at`     | TIMESTAMP    | NOT NULL, DEFAULT=NOW | 账户更新时间                                   |

### Enums

#### MerchantLevel
```python
class MerchantLevel(str, Enum):
    NORMAL = "normal"        # 普通商家（默认）
    VIP = "vip"              # VIP 商家（更低费率）
    DIAMOND = "diamond"      # 钻石商家（最低费率 + 专属服务）
```

#### MerchantStatus
```python
class MerchantStatus(str, Enum):
    ACTIVE = "active"        # 正常营业
    FROZEN = "frozen"        # 已冻结（违规冻结）
    CLOSED = "closed"        # 已注销（商家主动注销）
```

### Business Rules
- `merchant_id` 生成规则：`M + YYYYMMDD + 序号`（如 `M20250930001`）
- 账户创建时自动发送登录凭证（邮件/短信，未来 feature）
- `username` 默认使用申请表中的 `contact_phone` 或 `contact_email`
- 密码默认为随机生成的 8 位字符串，首次登录强制修改密码

### State Transitions
```
ACTIVE → FROZEN (平台管理员冻结)
ACTIVE → CLOSED (商家主动注销)
FROZEN → ACTIVE (解除冻结)
```

### Indexes
```sql
CREATE UNIQUE INDEX idx_merchant_account_merchant_id ON merchant_account(merchant_id);
CREATE UNIQUE INDEX idx_merchant_account_username ON merchant_account(username);
CREATE INDEX idx_merchant_account_level_status ON merchant_account(level, status);
CREATE INDEX idx_merchant_account_application_id ON merchant_account(application_id);
```

---

## 4. ContractFile (合同档案)

### Purpose
存储商家上传的线下签署合同照片（满足 FR-006，替代电子签名）。

### Fields

| Field         | Type         | Constraints           | Description                                    |
|---------------|--------------|-----------------------|------------------------------------------------|
| `id`          | UUID         | PRIMARY KEY           | 合同文件唯一标识                               |
| `merchant_id` | VARCHAR(20)  | NOT NULL, FK          | 关联商家账户 ID                                |
| `file_path`   | VARCHAR(500) | NOT NULL              | 文件存储路径（相对路径或 S3 Key）              |
| `file_size`   | BIGINT       | NOT NULL              | 文件大小（字节）                               |
| `file_type`   | VARCHAR(50)  | NOT NULL              | 文件类型（MIME type，如 `image/jpeg`）         |
| `upload_by`   | VARCHAR(100) | NOT NULL              | 上传人（商家用户名或平台管理员）               |
| `uploaded_at` | TIMESTAMP    | NOT NULL              | 上传时间                                       |
| `created_at`  | TIMESTAMP    | NOT NULL, DEFAULT=NOW | 记录创建时间                                   |

### Validation Rules
- `file_type`: 允许类型 `image/jpeg`, `image/png`, `application/pdf`
- `file_size`: 最大 10MB（10485760 字节）
- 文件内容验证：检查文件 Magic Bytes 防止伪造文件类型

### Business Rules
- 一个商家可以上传多份合同（如补充协议）
- 合同文件不可删除，仅支持标记为"已作废"（未来扩展字段 `is_void`）

### Indexes
```sql
CREATE INDEX idx_contract_file_merchant_id ON contract_file(merchant_id, uploaded_at DESC);
CREATE INDEX idx_contract_file_uploaded_at ON contract_file(uploaded_at DESC);
```

---

## 5. QualificationFile (资质文件)

### Purpose
存储商家申请时上传的资质证件（营业执照、身份证等），满足 FR-002。

### Fields

| Field            | Type         | Constraints           | Description                                        |
|------------------|--------------|-----------------------|----------------------------------------------------|
| `id`             | UUID         | PRIMARY KEY           | 资质文件唯一标识                                   |
| `application_id` | UUID         | NOT NULL, FK          | 关联商家申请 ID                                    |
| `merchant_id`    | VARCHAR(20)  | NULL, FK              | 关联商家账户 ID（审核通过后关联）                  |
| `file_type`      | ENUM         | NOT NULL              | 文件类型（见 QualificationFileType）               |
| `file_path`      | VARCHAR(500) | NOT NULL              | 文件存储路径                                       |
| `file_size`      | BIGINT       | NOT NULL              | 文件大小（字节）                                   |
| `audit_status`   | ENUM         | NOT NULL, DEFAULT='PENDING' | 审核状态（见 FileAuditStatus）                |
| `uploaded_at`    | TIMESTAMP    | NOT NULL              | 上传时间                                           |
| `created_at`     | TIMESTAMP    | NOT NULL, DEFAULT=NOW | 记录创建时间                                       |

### Enums

#### QualificationFileType
```python
class QualificationFileType(str, Enum):
    BUSINESS_LICENSE = "business_license"      # 营业执照
    ID_CARD_FRONT = "id_card_front"            # 身份证正面
    ID_CARD_BACK = "id_card_back"              # 身份证背面
    OTHER = "other"                            # 其他资质文件
```

#### FileAuditStatus
```python
class FileAuditStatus(str, Enum):
    PENDING = "pending"              # 待审核
    APPROVED = "approved"            # 审核通过
    REJECTED = "rejected"            # 审核拒绝（如文件不清晰）
```

### Validation Rules
- 每个 `application_id` 必须上传至少 3 个文件：`BUSINESS_LICENSE`, `ID_CARD_FRONT`, `ID_CARD_BACK`
- `file_type` 允许 `image/jpeg`, `image/png`, `application/pdf`
- `file_size`: 最大 10MB

### Business Rules
- 审核员可以单独审核每个文件（标记为 `APPROVED` 或 `REJECTED`）
- 如果任何必需文件被 `REJECTED`，整个申请状态变更为 `REQUIRE_SUPPLEMENT`
- 商家补充材料时，可以重新上传被拒绝的文件

### Indexes
```sql
CREATE INDEX idx_qualification_file_application_id ON qualification_file(application_id, file_type);
CREATE INDEX idx_qualification_file_merchant_id ON qualification_file(merchant_id);
CREATE INDEX idx_qualification_file_audit_status ON qualification_file(audit_status);
```

---

## Data Integrity & Constraints

### Foreign Key Relationships
```sql
-- AuditRecord → MerchantApplication
ALTER TABLE audit_record ADD CONSTRAINT fk_audit_record_application
  FOREIGN KEY (application_id) REFERENCES merchant_application(id) ON DELETE CASCADE;

-- MerchantAccount → MerchantApplication
ALTER TABLE merchant_account ADD CONSTRAINT fk_merchant_account_application
  FOREIGN KEY (application_id) REFERENCES merchant_application(id) ON DELETE RESTRICT;

-- ContractFile → MerchantAccount
ALTER TABLE contract_file ADD CONSTRAINT fk_contract_file_merchant
  FOREIGN KEY (merchant_id) REFERENCES merchant_account(merchant_id) ON DELETE CASCADE;

-- QualificationFile → MerchantApplication
ALTER TABLE qualification_file ADD CONSTRAINT fk_qualification_file_application
  FOREIGN KEY (application_id) REFERENCES merchant_application(id) ON DELETE CASCADE;

-- QualificationFile → MerchantAccount (optional)
ALTER TABLE qualification_file ADD CONSTRAINT fk_qualification_file_merchant
  FOREIGN KEY (merchant_id) REFERENCES merchant_account(merchant_id) ON DELETE SET NULL;
```

### Check Constraints
```sql
-- 确保提交时间晚于创建时间
ALTER TABLE merchant_application ADD CONSTRAINT chk_submitted_after_created
  CHECK (submitted_at IS NULL OR submitted_at >= created_at);

-- 确保文件大小合理
ALTER TABLE contract_file ADD CONSTRAINT chk_file_size_positive
  CHECK (file_size > 0 AND file_size <= 10485760);

ALTER TABLE qualification_file ADD CONSTRAINT chk_file_size_positive
  CHECK (file_size > 0 AND file_size <= 10485760);
```

---

## Migration Strategy

### Alembic Migration Files
```python
# alembic/versions/001_create_merchant_tables.py
def upgrade():
    # 创建 ENUM 类型
    application_status = sa.Enum(
        'draft', 'pending', 'under_review', 'require_supplement',
        'approved', 'rejected', name='application_status'
    )
    application_status.create(op.get_bind(), checkfirst=True)

    # 创建 merchant_application 表
    op.create_table(
        'merchant_application',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('business_name', sa.String(200), nullable=False),
        # ... 其他字段
    )

    # 创建索引
    op.create_index('idx_merchant_application_status', 'merchant_application',
                    ['status', 'created_at'])

def downgrade():
    op.drop_table('merchant_application')
    sa.Enum(name='application_status').drop(op.get_bind(), checkfirst=True)
```

---

## Summary

本数据模型设计：
1. ✅ 覆盖所有 Spec 中的 Key Entities（商家申请、审核记录、商家账户、合同档案、资质文件）
2. ✅ 支持完整的业务流程（申请 → 审核 → 账户创建 → 合同存档）
3. ✅ 遵循 Constitution 原则（多租户隔离、审计追踪、数据加密）
4. ✅ 包含详细的验证规则、状态转换和索引策略
5. ✅ 使用 PostgreSQL 高级特性（JSONB、ENUM、全文搜索）

**下一步**: 生成 API 契约（OpenAPI schemas）。