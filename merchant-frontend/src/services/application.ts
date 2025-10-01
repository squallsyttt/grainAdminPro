/**
 * 商家申请管理 API 服务（商家端）
 */
import { request } from '@/utils/request';

/** 申请状态枚举 */
export enum ApplicationStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  UNDER_REVIEW = 'under_review',
  REQUIRE_SUPPLEMENT = 'require_supplement',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

/** 申请信息 */
export interface Application {
  id: string;
  business_name: string;
  unified_social_credit: string;
  legal_person_name: string;
  legal_person_id_number?: string;
  contact_name: string;
  contact_phone: string;
  contact_email: string;
  business_categories: string[];
  status: ApplicationStatus;
  submitted_at?: string;
  created_at: string;
  updated_at: string;
}

/** 创建申请请求 */
export interface CreateApplicationRequest {
  business_name: string;
  unified_social_credit: string;
  legal_person_name: string;
  legal_person_id_number: string;
  contact_name: string;
  contact_phone: string;
  contact_email: string;
  business_categories: string[];
}

/**
 * 创建申请
 */
export async function createApplication(data: CreateApplicationRequest) {
  return request<{ data: Application }>('/api/v1/applications', {
    method: 'POST',
    data,
  });
}

/**
 * 查询我的申请列表
 */
export async function getMyApplications() {
  return request<{ data: { items: Application[] } }>('/api/v1/applications', {
    method: 'GET',
  });
}

/**
 * 查询申请详情
 */
export async function getApplication(id: string) {
  return request<{ data: Application }>(`/api/v1/applications/${id}`, {
    method: 'GET',
  });
}

/**
 * 更新申请
 */
export async function updateApplication(id: string, data: Partial<CreateApplicationRequest>) {
  return request<{ data: Application }>(`/api/v1/applications/${id}`, {
    method: 'PUT',
    data,
  });
}

/**
 * 提交申请
 */
export async function submitApplication(id: string) {
  return request<{ data: Application }>(`/api/v1/applications/${id}/submit`, {
    method: 'POST',
  });
}