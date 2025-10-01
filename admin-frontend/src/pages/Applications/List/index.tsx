/**
 * 商家申请列表页面
 *
 * 功能：
 * - 展示所有商家申请列表
 * - 支持按状态筛选
 * - 支持分页
 * - 可查看申请详情
 */
import React, { useRef } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { Badge, Button } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { useNavigate } from '@umijs/max';
import dayjs from 'dayjs';
import type { Application } from '@/services/application';
import { ApplicationStatus, listApplications } from '@/services/application';

/**
 * 申请状态映射
 */
const StatusMap: Record<ApplicationStatus, { text: string; status: 'default' | 'processing' | 'success' | 'error' | 'warning' }> = {
  [ApplicationStatus.DRAFT]: { text: '草稿', status: 'default' },
  [ApplicationStatus.PENDING]: { text: '待审核', status: 'processing' },
  [ApplicationStatus.UNDER_REVIEW]: { text: '审核中', status: 'processing' },
  [ApplicationStatus.REQUIRE_SUPPLEMENT]: { text: '需补充材料', status: 'warning' },
  [ApplicationStatus.APPROVED]: { text: '已通过', status: 'success' },
  [ApplicationStatus.REJECTED]: { text: '已拒绝', status: 'error' },
};

/**
 * 商家申请列表页面
 */
const ApplicationList: React.FC = () => {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();

  /**
   * 表格列定义
   */
  const columns: ProColumns<Application>[] = [
    {
      title: '企业名称',
      dataIndex: 'business_name',
      width: 200,
      ellipsis: true,
      search: false,
    },
    {
      title: '统一社会信用代码',
      dataIndex: 'unified_social_credit',
      width: 180,
      search: false,
      copyable: true,
    },
    {
      title: '法人姓名',
      dataIndex: 'legal_person_name',
      width: 100,
      search: false,
    },
    {
      title: '联系人',
      dataIndex: 'contact_name',
      width: 100,
      search: false,
    },
    {
      title: '联系电话',
      dataIndex: 'contact_phone',
      width: 120,
      search: false,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 120,
      valueType: 'select',
      valueEnum: Object.fromEntries(
        Object.entries(ApplicationStatus).map(([, value]) => [
          value,
          { text: StatusMap[value].text },
        ])
      ),
      render: (_, record) => {
        const status = StatusMap[record.status];
        return <Badge status={status.status} text={status.text} />;
      },
    },
    {
      title: '提交时间',
      dataIndex: 'submitted_at',
      width: 160,
      search: false,
      valueType: 'dateTime',
      render: (_, record) => {
        return record.submitted_at
          ? dayjs(record.submitted_at).format('YYYY-MM-DD HH:mm:ss')
          : '-';
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 160,
      search: false,
      valueType: 'dateTime',
      render: (_, record) => dayjs(record.created_at).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      dataIndex: 'option',
      valueType: 'option',
      width: 120,
      fixed: 'right',
      render: (_, record) => [
        <Button
          key="detail"
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => navigate(`/applications/detail/${record.id}`)}
        >
          查看详情
        </Button>,
      ],
    },
  ];

  return (
    <PageContainer
      title="商家申请管理"
      content="查看和管理所有商家入驻申请"
    >
      <ProTable<Application>
        columns={columns}
        actionRef={actionRef}
        cardBordered
        request={async (params) => {
          try {
            const response = await listApplications({
              page: params.current || 1,
              page_size: params.pageSize || 20,
              status: params.status as ApplicationStatus,
            });

            return {
              data: response.data.items,
              total: response.data.total,
              success: true,
            };
          } catch (error) {
            console.error('Failed to load applications:', error);
            return {
              data: [],
              total: 0,
              success: false,
            };
          }
        }}
        rowKey="id"
        search={{
          labelWidth: 'auto',
          defaultCollapsed: false,
        }}
        options={{
          search: true,
          reload: true,
          density: true,
          setting: true,
        }}
        form={{
          syncToUrl: true,
          syncToInitialValues: false,
        }}
        pagination={{
          pageSize: 20,
          showQuickJumper: true,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
        }}
        dateFormatter="string"
        headerTitle="申请列表"
        toolBarRender={() => [
          <Button
            key="refresh"
            type="primary"
            onClick={() => actionRef.current?.reload()}
          >
            刷新
          </Button>,
        ]}
      />
    </PageContainer>
  );
};

export default ApplicationList;