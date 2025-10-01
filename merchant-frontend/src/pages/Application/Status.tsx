/**
 * 申请状态查询页面
 *
 * 功能：
 * - 显示当前申请状态（Steps组件）
 * - 显示审核历史（Timeline）
 * - 补充材料按钮
 */
import React, { useState, useEffect } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Card, Steps, Timeline, Tag, Button, Empty, Spin } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';
import dayjs from 'dayjs';
import { getMyApplications, ApplicationStatus } from '@/services/application';
import type { Application } from '@/services/application';

/**
 * 状态步骤映射
 */
const StatusStepMap: Record<ApplicationStatus, number> = {
  [ApplicationStatus.DRAFT]: 0,
  [ApplicationStatus.PENDING]: 1,
  [ApplicationStatus.UNDER_REVIEW]: 2,
  [ApplicationStatus.REQUIRE_SUPPLEMENT]: 2,
  [ApplicationStatus.APPROVED]: 3,
  [ApplicationStatus.REJECTED]: 2,
};

/**
 * 状态文本映射
 */
const StatusText: Record<ApplicationStatus, string> = {
  [ApplicationStatus.DRAFT]: '草稿',
  [ApplicationStatus.PENDING]: '待审核',
  [ApplicationStatus.UNDER_REVIEW]: '审核中',
  [ApplicationStatus.REQUIRE_SUPPLEMENT]: '需补充材料',
  [ApplicationStatus.APPROVED]: '审核通过',
  [ApplicationStatus.REJECTED]: '审核拒绝',
};

/**
 * 申请状态页面
 */
const StatusPage: React.FC = () => {
  const [application, setApplication] = useState<Application | null>(null);
  const [loading, setLoading] = useState(false);

  /**
   * 加载申请信息
   */
  useEffect(() => {
    loadApplication();
  }, []);

  /**
   * 获取我的申请
   */
  const loadApplication = async () => {
    setLoading(true);
    try {
      const response = await getMyApplications();
      if (response.data.items.length > 0) {
        setApplication(response.data.items[0]); // 取第一个申请
      }
    } catch (error) {
      console.error('Failed to load application:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 获取步骤状态
   */
  const getStepStatus = (step: number): 'wait' | 'process' | 'finish' | 'error' => {
    if (!application) return 'wait';

    const currentStep = StatusStepMap[application.status];

    if (application.status === ApplicationStatus.REJECTED) {
      return step === currentStep ? 'error' : step < currentStep ? 'finish' : 'wait';
    }

    if (step < currentStep) return 'finish';
    if (step === currentStep) return 'process';
    return 'wait';
  };

  if (loading) {
    return (
      <PageContainer title="申请状态">
        <Card>
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spin size="large" />
          </div>
        </Card>
      </PageContainer>
    );
  }

  if (!application) {
    return (
      <PageContainer title="申请状态">
        <Card>
          <Empty
            description="您还没有提交申请"
            style={{ padding: '50px 0' }}
          >
            <Button type="primary" onClick={() => history.push('/application/create')}>
              立即申请
            </Button>
          </Empty>
        </Card>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title="申请状态"
      content={`企业名称：${application.business_name}`}
    >
      {/* 申请状态流程 */}
      <Card title="申请进度" bordered={false} style={{ marginBottom: 24 }}>
        <Steps
          current={StatusStepMap[application.status]}
          status={getStepStatus(StatusStepMap[application.status])}
        >
          <Steps.Step
            title="提交申请"
            description="填写企业信息"
            icon={getStepStatus(0) === 'finish' ? <CheckCircleOutlined /> : undefined}
          />
          <Steps.Step
            title="等待审核"
            description="平台审核中"
            icon={getStepStatus(1) === 'process' ? <ClockCircleOutlined /> : undefined}
          />
          <Steps.Step
            title="审核处理"
            description="审核员处理"
            icon={
              application.status === ApplicationStatus.REJECTED ? (
                <CloseCircleOutlined />
              ) : getStepStatus(2) === 'process' ? (
                <ClockCircleOutlined />
              ) : undefined
            }
          />
          <Steps.Step
            title="审核完成"
            description={StatusText[application.status]}
            icon={
              application.status === ApplicationStatus.APPROVED ? (
                <CheckCircleOutlined />
              ) : undefined
            }
          />
        </Steps>
      </Card>

      {/* 申请详情 */}
      <Card title="申请详情" bordered={false} style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <strong>当前状态：</strong>
          <Tag
            color={
              application.status === ApplicationStatus.APPROVED
                ? 'success'
                : application.status === ApplicationStatus.REJECTED
                ? 'error'
                : 'processing'
            }
          >
            {StatusText[application.status]}
          </Tag>
        </div>
        <div style={{ marginBottom: 16 }}>
          <strong>统一社会信用代码：</strong>
          {application.unified_social_credit}
        </div>
        <div style={{ marginBottom: 16 }}>
          <strong>提交时间：</strong>
          {application.submitted_at
            ? dayjs(application.submitted_at).format('YYYY-MM-DD HH:mm:ss')
            : '-'}
        </div>
        <div>
          <strong>更新时间：</strong>
          {dayjs(application.updated_at).format('YYYY-MM-DD HH:mm:ss')}
        </div>
      </Card>

      {/* 操作按钮 */}
      {application.status === ApplicationStatus.REQUIRE_SUPPLEMENT && (
        <Card title="下一步操作" bordered={false}>
          <Button
            type="primary"
            size="large"
            onClick={() => history.push(`/application/edit/${application.id}`)}
          >
            补充材料
          </Button>
        </Card>
      )}
    </PageContainer>
  );
};

export default StatusPage;