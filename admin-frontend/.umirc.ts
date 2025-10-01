import { defineConfig } from '@umijs/max';

export default defineConfig({
  // 禁用 MFSU 以解决模块加载错误
  mfsu: false,
  // 代理配置
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
  // 路由配置
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
      path: '/audits',
      name: '审核管理',
      icon: 'AuditOutlined',
      routes: [
        {
          path: '/audits/history/:id',
          name: '审核历史',
          hideInMenu: true,
          component: './Audits/History',
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
  // 标题
  title: 'grainAdmin 主后台',
});