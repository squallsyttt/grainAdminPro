/**
 * 审核管理 API 服务
 */
import { request } from '@/utils/request';

/** 审核动作枚举 */
export enum AuditAction {
  START_REVIEW = 'start_review',
  APPROVE = 'approve',
  REJECT = 'reject',
  REQUEST_SUPPLEMENT = 'request_supplement',
}

/** 审核结果枚举 */
export enum AuditResult {
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PENDING_SUPPLEMENT = 'pending_supplement',
  IN_PROGRESS = 'in_progress',
}

/** 审核记录 */
export interface AuditRecord {
  id: string;
  application_id: string;
  auditor_id: string;
  auditor_name: string;
  action: AuditAction;
  result: AuditResult;
  comment?: string;
  created_at: string;
}

/** 创建审核请求 */
export interface CreateAuditRequest {
  application_id: string;
  action: AuditAction;
  result: AuditResult;
  comment?: string;
}

/**
 * 创建审核记录（提交审核操作）
 */
export async function createAudit(data: CreateAuditRequest) {
  return request<{ data: AuditRecord }>('/api/v1/audits', {
    method: 'POST',
    data,
  });
}

/**
 * 查询审核历史
 */
export async function getAuditHistory(applicationId: string) {
  return request<{ data: AuditRecord[] }>(`/api/v1/audits/history/${applicationId}`, {
    method: 'GET',
  });
}