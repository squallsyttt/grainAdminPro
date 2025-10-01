import { defineConfig } from '@umijs/max';

export default defineConfig({
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
      redirect: '/application/status',
    },
    {
      path: '/login',
      component: './Login',
      layout: false,
    },
    {
      path: '/application',
      name: '入驻申请',
      icon: 'FormOutlined',
      routes: [
        {
          path: '/application/create',
          name: '提交申请',
          component: './Application/Create',
        },
        {
          path: '/application/status',
          name: '申请状态',
          component: './Application/Status',
        },
      ],
    },
    {
      path: '/contracts',
      name: '合同管理',
      icon: 'FileTextOutlined',
      routes: [
        {
          path: '/contracts/upload',
          name: '上传合同',
          component: './Contracts/Upload',
        },
      ],
    },
  ],
  npmClient: 'npm',
  // 标题
  title: 'grainAdmin 商家后台',
});