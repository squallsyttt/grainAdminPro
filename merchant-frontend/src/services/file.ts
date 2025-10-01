/**
 * 文件上传 API 服务
 */
import { request } from '@/utils/request';

/** 文件信息 */
export interface FileInfo {
  id: string;
  file_path: string;
  file_size: number;
  file_type: string;
  uploaded_at: string;
}

/**
 * 上传文件
 */
export async function uploadFile(file: File, fileType: string, applicationId?: string) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('file_type', fileType);
  if (applicationId) {
    formData.append('application_id', applicationId);
  }

  return request<{ data: FileInfo }>('/api/v1/files/upload', {
    method: 'POST',
    data: formData,
    requestType: 'form',
  });
}