/**
 * 请求工具封装
 * 基于 axios 实现
 */
import axios, { AxiosRequestConfig } from 'axios';
import { message } from 'antd';

const instance = axios.create({
  timeout: 10000,
});

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // TODO: 添加 token
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const errorMessage = error.response?.data?.message || '请求失败';
    message.error(errorMessage);
    return Promise.reject(error);
  }
);

/**
 * 通用请求方法
 */
export async function request<T = any>(
  url: string,
  options: AxiosRequestConfig = {}
): Promise<T> {
  return instance.request<any, T>({
    url,
    ...options,
  });
}

export default request;