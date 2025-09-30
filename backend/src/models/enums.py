"""
数据库枚举类型定义
包含所有业务状态和类型的枚举值
"""
from enum import Enum


class ApplicationStatus(str, Enum):
    """商家申请状态"""

    DRAFT = "draft"  # 草稿（商家填写中）
    PENDING = "pending"  # 待审核（已提交）
    UNDER_REVIEW = "under_review"  # 审核中（审核员正在处理）
    REQUIRE_SUPPLEMENT = "require_supplement"  # 要求补充材料
    APPROVED = "approved"  # 审核通过
    REJECTED = "rejected"  # 审核拒绝


class AuditAction(str, Enum):
    """审核动作"""

    START_REVIEW = "start_review"  # 开始审核
    APPROVE = "approve"  # 审核通过
    REJECT = "reject"  # 审核拒绝
    REQUEST_SUPPLEMENT = "request_supplement"  # 要求补充材料


class AuditResult(str, Enum):
    """审核结果"""

    APPROVED = "approved"  # 通过
    REJECTED = "rejected"  # 拒绝
    PENDING_SUPPLEMENT = "pending_supplement"  # 待补充材料
    IN_PROGRESS = "in_progress"  # 审核中（开始审核时）


class MerchantLevel(str, Enum):
    """商家等级"""

    NORMAL = "normal"  # 普通商家（默认）
    VIP = "vip"  # VIP 商家（更低费率）
    DIAMOND = "diamond"  # 钻石商家（最低费率 + 专属服务）


class MerchantStatus(str, Enum):
    """商家账户状态"""

    ACTIVE = "active"  # 正常营业
    FROZEN = "frozen"  # 已冻结（违规冻结）
    CLOSED = "closed"  # 已注销（商家主动注销）


class QualificationFileType(str, Enum):
    """资质文件类型"""

    BUSINESS_LICENSE = "business_license"  # 营业执照
    ID_CARD_FRONT = "id_card_front"  # 身份证正面
    ID_CARD_BACK = "id_card_back"  # 身份证背面
    OTHER = "other"  # 其他资质文件


class FileAuditStatus(str, Enum):
    """文件审核状态"""

    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 审核通过
    REJECTED = "rejected"  # 审核拒绝（如文件不清晰）