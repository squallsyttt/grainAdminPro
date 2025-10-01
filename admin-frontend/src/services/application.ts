/**
 * 商家申请管理 API 服务
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
  contact_name: string;
  contact_phone: string;
  contact_email: string;
  business_categories: string[];
  status: ApplicationStatus;
  submitted_at?: string;
  created_at: string;
  updated_at: string;
}

/** 申请列表响应 */
export interface ApplicationListResponse {
  items: Application[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/** 查询申请列表参数 */
export interface ListApplicationsParams {
  status?: ApplicationStatus;
  page?: number;
  page_size?: number;
}

/**
 * 查询商家申请列表
 */
export async function listApplications(params: ListApplicationsParams = {}) {
  return request<{ data: ApplicationListResponse }>('/api/v1/applications', {
    method: 'GET',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 20,
      ...(params.status && { status: params.status }),
    },
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
 * 创建申请
 */
export async function createApplication(data: Partial<Application>) {
  return request<{ data: Application }>('/api/v1/applications', {
    method: 'POST',
    data,
  });
}

/**
 * 更新申请
 */
export async function updateApplication(id: string, data: Partial<Application>) {
  return request<{ data: Application }>(`/api/v1/applications/${id}`, {
    method: 'PUT',
    data,
  });
}