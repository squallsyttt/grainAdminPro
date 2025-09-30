// 运行时配置文件
export const request = {
  timeout: 10000,
  errorConfig: {
    errorHandler: (error: any) => {
      console.error('请求错误:', error);
      throw error;
    },
  },
  requestInterceptors: [
    (url: string, options: any) => {
      // 添加认证 token
      const token = localStorage.getItem('token');
      if (token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token}`,
        };
      }
      return { url, options };
    },
  ],
};