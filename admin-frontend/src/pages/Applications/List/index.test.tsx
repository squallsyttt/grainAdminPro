/**
 * ApplicationList 组件单元测试
 */
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ApplicationList from './index';
import * as applicationService from '@/services/application';

// Mock services
jest.mock('@/services/application');

// Mock Ant Design Pro Components
jest.mock('@ant-design/pro-components', () => ({
  PageContainer: ({ children }: any) => <div>{children}</div>,
  ProTable: ({ columns, headerTitle }: any) => {
    // 模拟简单的表格渲染
    return (
      <div data-testid="pro-table">
        <h3>{headerTitle}</h3>
        {columns.map((col: any) => (
          <div key={col.dataIndex || col.title}>{col.title}</div>
        ))}
      </div>
    );
  },
}));

describe('ApplicationList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该正确渲染申请列表页面', () => {
    render(
      <BrowserRouter>
        <ApplicationList />
      </BrowserRouter>
    );

    // 验证页面标题
    expect(screen.getByText('申请列表')).toBeInTheDocument();
  });

  it('应该显示正确的表格列', () => {
    render(
      <BrowserRouter>
        <ApplicationList />
      </BrowserRouter>
    );

    // 验证表格列存在
    expect(screen.getByText('企业名称')).toBeInTheDocument();
    expect(screen.getByText('联系人')).toBeInTheDocument();
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('提交时间')).toBeInTheDocument();
  });

  it('应该能够调用API获取申请列表数据', async () => {
    const mockData = {
      data: {
        items: [
          {
            id: '1',
            business_name: '测试企业',
            unified_social_credit: '12345678901234567X',
            legal_person_name: '张三',
            contact_name: '李四',
            contact_phone: '13800138000',
            contact_email: 'test@example.com',
            business_categories: ['食品'],
            status: 'pending',
            created_at: '2025-09-30T10:00:00Z',
            updated_at: '2025-09-30T10:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        total_pages: 1,
      },
    };

    (applicationService.listApplications as jest.Mock).mockResolvedValue(mockData);

    render(
      <BrowserRouter>
        <ApplicationList />
      </BrowserRouter>
    );

    // ProTable会在mount时调用request函数
    await waitFor(() => {
      expect(applicationService.listApplications).toHaveBeenCalled();
    });
  });
});