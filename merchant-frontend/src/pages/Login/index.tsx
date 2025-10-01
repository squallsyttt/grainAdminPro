/**
 * 登录页面（商家端）
 */
import React from 'react';
import { Form, Input, Button, Card } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';

const Login: React.FC = () => {
  const onFinish = (values: any) => {
    console.log('登录:', values);
    // TODO: 实现登录逻辑
    // 暂时直接跳转到首页
    history.push('/application/status');
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: '#f0f2f5'
    }}>
      <Card
        title="grainAdmin 商家后台登录"
        style={{ width: 400 }}
      >
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large">
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;