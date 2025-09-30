import { defineConfig } from '@umijs/max';

export default defineConfig({
  antd: {
    // Ant Design 配置
    configProvider: {},
  },
  request: {
    // 请求配置
    dataField: 'data',
  },
  locale: {
    // 国际化配置
    default: 'zh-CN',
    baseSeparator: '-',
  },
  model: {},
  initialState: {},
  proxy: {
    // 开发代理配置
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
  routes: [
    {
      path: '/',
      redirect: '/apply',
    },
    {
      path: '/login',
      component: './Login',
      layout: false,
    },
    {
      path: '/apply',
      name: '入驻申请',
      icon: 'FormOutlined',
      component: './Apply',
    },
    {
      path: '/info',
      name: '店铺信息',
      icon: 'ShopOutlined',
      component: './Info',
    },
    {
      path: '/contracts',
      name: '合同管理',
      icon: 'FileTextOutlined',
      component: './Contracts',
    },
  ],
  npmClient: 'npm',
});