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
      redirect: '/applications',
    },
    {
      path: '/login',
      component: './Login',
      layout: false,
    },
    {
      path: '/applications',
      name: '商家申请',
      icon: 'ShopOutlined',
      routes: [
        {
          path: '/applications',
          redirect: '/applications/list',
        },
        {
          path: '/applications/list',
          name: '申请列表',
          component: './Applications/List',
        },
        {
          path: '/applications/detail/:id',
          name: '申请详情',
          hideInMenu: true,
          component: './Applications/Detail',
        },
      ],
    },
    {
      path: '/merchants',
      name: '商家管理',
      icon: 'TeamOutlined',
      component: './Merchants',
    },
  ],
  npmClient: 'npm',
});