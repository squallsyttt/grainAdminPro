/**
 * 申请详情展示组件
 */
import React from 'react';
import { Descriptions, Card, Tag, Space } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import type { Application } from '@/services/application';
import { ApplicationStatus } from '@/services/application';

interface ApplicationDetailProps {
  application: Application;
}

/** 状态图标映射 */
const StatusIcon: Record<ApplicationStatus, React.ReactElement> = {
  [ApplicationStatus.DRAFT]: <ClockCircleOutlined style={{ color: '#999' }} />,
  [ApplicationStatus.PENDING]: <ClockCircleOutlined style={{ color: '#1890ff' }} />,
  [ApplicationStatus.UNDER_REVIEW]: <ClockCircleOutlined style={{ color: '#1890ff' }} />,
  [ApplicationStatus.REQUIRE_SUPPLEMENT]: <ClockCircleOutlined style={{ color: '#faad14' }} />,
  [ApplicationStatus.APPROVED]: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  [ApplicationStatus.REJECTED]: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
};

/** 状态文本映射 */
const StatusText: Record<ApplicationStatus, string> = {
  [ApplicationStatus.DRAFT]: '草稿',
  [ApplicationStatus.PENDING]: '待审核',
  [ApplicationStatus.UNDER_REVIEW]: '审核中',
  [ApplicationStatus.REQUIRE_SUPPLEMENT]: '需补充材料',
  [ApplicationStatus.APPROVED]: '已通过',
  [ApplicationStatus.REJECTED]: '已拒绝',
};

/**
 * 申请详情组件
 */
const ApplicationDetail: React.FC<ApplicationDetailProps> = ({ application }) => {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* 企业基本信息 */}
      <Card title="企业基本信息" bordered={false}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="企业名称">
            {application.business_name}
          </Descriptions.Item>
          <Descriptions.Item label="统一社会信用代码">
            {application.unified_social_credit}
          </Descriptions.Item>
          <Descriptions.Item label="经营类目" span={2}>
            {application.business_categories.map((category) => (
              <Tag key={category} color="blue">
                {category}
              </Tag>
            ))}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 法人信息 */}
      <Card title="法人信息" bordered={false}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="法人姓名">
            {application.legal_person_name}
          </Descriptions.Item>
          <Descriptions.Item label="法人身份证号">
            {/* 出于隐私考虑，仅显示部分信息 */}
            {application.contact_phone || '***************'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 联系方式 */}
      <Card title="联系方式" bordered={false}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="联系人姓名">
            {application.contact_name}
          </Descriptions.Item>
          <Descriptions.Item label="联系电话">
            {application.contact_phone}
          </Descriptions.Item>
          <Descriptions.Item label="联系邮箱" span={2}>
            {application.contact_email}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 申请状态 */}
      <Card title="申请状态" bordered={false}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="当前状态">
            <Space>
              {StatusIcon[application.status]}
              {StatusText[application.status]}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="提交时间">
            {application.submitted_at
              ? dayjs(application.submitted_at).format('YYYY-MM-DD HH:mm:ss')
              : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {dayjs(application.created_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {dayjs(application.updated_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </Space>
  );
};

export default ApplicationDetail;