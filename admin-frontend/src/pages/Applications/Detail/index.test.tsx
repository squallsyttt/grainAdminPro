/**
 * ApplicationAudit 组件单元测试
 */
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ApplicationAudit from './index';
import * as applicationService from '@/services/application';
import { ApplicationStatus } from '@/services/application';

// Mock services
jest.mock('@/services/application');

// Mock components
jest.mock('@ant-design/pro-components', () => ({
  PageContainer: ({ children, title }: any) => (
    <div>
      <h1>{title}</h1>
      {children}
    </div>
  ),
}));

jest.mock('@/components/ApplicationDetail', () => ({
  __esModule: true,
  default: () => <div data-testid="application-detail">Application Detail</div>,
}));

jest.mock('@umijs/max', () => ({
  history: {
    push: jest.fn(),
    back: jest.fn(),
  },
  useParams: () => ({ id: 'test-id-123' }),
}));

describe('ApplicationAudit', () => {
  const mockApplication = {
    id: 'test-id-123',
    business_name: '测试企业',
    unified_social_credit: '12345678901234567X',
    legal_person_name: '张三',
    contact_name: '李四',
    contact_phone: '13800138000',
    contact_email: 'test@example.com',
    business_categories: ['食品'],
    status: ApplicationStatus.PENDING,
    created_at: '2025-09-30T10:00:00Z',
    updated_at: '2025-09-30T10:00:00Z',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (applicationService.getApplication as jest.Mock).mockResolvedValue({
      data: mockApplication,
    });
  });

  it('应该正确渲染审核页面', async () => {
    render(
      <BrowserRouter>
        <ApplicationAudit />
      </BrowserRouter>
    );

    // 等待数据加载
    await waitFor(() => {
      expect(applicationService.getApplication).toHaveBeenCalledWith('test-id-123');
    });

    // 验证页面标题
    expect(screen.getByText('申请审核')).toBeInTheDocument();

    // 验证申请详情组件已渲染
    expect(screen.getByTestId('application-detail')).toBeInTheDocument();
  });

  it('应该显示审核操作按钮（当状态为PENDING时）', async () => {
    render(
      <BrowserRouter>
        <ApplicationAudit />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('审核通过')).toBeInTheDocument();
    });

    expect(screen.getByText('审核拒绝')).toBeInTheDocument();
    expect(screen.getByText('要求补充材料')).toBeInTheDocument();
  });

  it('应该能够打开审核Modal', async () => {
    render(
      <BrowserRouter>
        <ApplicationAudit />
      </BrowserRouter>
    );

    // 等待页面加载
    await waitFor(() => {
      expect(screen.getByText('审核通过')).toBeInTheDocument();
    });

    // 点击审核通过按钮
    fireEvent.click(screen.getByText('审核通过'));

    // 验证Modal打开
    await waitFor(() => {
      expect(screen.getByText('通过申请')).toBeInTheDocument();
    });
  });
});