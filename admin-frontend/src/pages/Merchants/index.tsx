/**
 * 商家管理页面
 */
import React from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Card } from 'antd';

const Merchants: React.FC = () => {
  return (
    <PageContainer
      title="商家管理"
      content="管理已入驻的商家账户"
    >
      <Card>
        <div style={{ padding: '50px', textAlign: 'center', color: '#999' }}>
          商家管理功能开发中...
        </div>
      </Card>
    </PageContainer>
  );
};

export default Merchants;