/**
 * 审核历史页面
 *
 * 功能：
 * - Timeline时间轴显示审核记录
 * - 显示审核员、操作、结果、意见、时间
 */
import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Card, Timeline, Tag, Empty, Spin, Button } from 'antd';
import { ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { history, useParams } from '@umijs/max';
import dayjs from 'dayjs';
import type { AuditRecord } from '@/services/audit';
import { getAuditHistory, AuditAction, AuditResult } from '@/services/audit';

/**
 * 审核动作图标映射
 */
const ActionIcon: Record<AuditAction, React.ReactElement> = {
  [AuditAction.START_REVIEW]: <ClockCircleOutlined style={{ color: '#1890ff' }} />,
  [AuditAction.APPROVE]: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  [AuditAction.REJECT]: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
  [AuditAction.REQUEST_SUPPLEMENT]: <ExclamationCircleOutlined style={{ color: '#faad14' }} />,
};

/**
 * 审核动作文本映射
 */
const ActionText: Record<AuditAction, string> = {
  [AuditAction.START_REVIEW]: '开始审核',
  [AuditAction.APPROVE]: '审核通过',
  [AuditAction.REJECT]: '审核拒绝',
  [AuditAction.REQUEST_SUPPLEMENT]: '要求补充材料',
};

/**
 * 审核结果颜色映射
 */
const ResultColor: Record<AuditResult, string> = {
  [AuditResult.IN_PROGRESS]: 'processing',
  [AuditResult.APPROVED]: 'success',
  [AuditResult.REJECTED]: 'error',
  [AuditResult.PENDING_SUPPLEMENT]: 'warning',
};

/**
 * 审核结果文本映射
 */
const ResultText: Record<AuditResult, string> = {
  [AuditResult.IN_PROGRESS]: '审核中',
  [AuditResult.APPROVED]: '已通过',
  [AuditResult.REJECTED]: '已拒绝',
  [AuditResult.PENDING_SUPPLEMENT]: '待补充',
};

/**
 * 审核历史页面
 */
const AuditHistory: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [auditRecords, setAuditRecords] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(false);

  /**
   * 获取审核历史
   */
  const loadAuditHistory = useCallback(async () => {
    if (!id) return;

    setLoading(true);
    try {
      const response = await getAuditHistory(id);
      setAuditRecords(response.data);
    } catch (error) {
      console.error('Failed to load audit history:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  /**
   * 加载审核历史
   */
  useEffect(() => {
    if (id) {
      loadAuditHistory();
    }
  }, [id, loadAuditHistory]);

  return (
    <PageContainer
      title="审核历史"
      onBack={() => history.back()}
      extra={[
        <Button
          key="back"
          icon={<ArrowLeftOutlined />}
          onClick={() => history.push('/applications/list')}
        >
          返回列表
        </Button>,
      ]}
    >
      <Card bordered={false}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spin size="large" />
          </div>
        ) : auditRecords.length === 0 ? (
          <Empty description="暂无审核记录" />
        ) : (
          <Timeline>
            {auditRecords.map((record) => (
              <Timeline.Item
                key={record.id}
                dot={ActionIcon[record.action]}
                color={ResultColor[record.result]}
              >
                <div style={{ paddingBottom: 16 }}>
                  <div style={{ marginBottom: 8 }}>
                    <Tag color={ResultColor[record.result]}>
                      {ResultText[record.result]}
                    </Tag>
                    <strong>{ActionText[record.action]}</strong>
                  </div>
                  <div style={{ color: '#666', marginBottom: 8 }}>
                    审核员：{record.auditor_name || record.auditor_id}
                  </div>
                  {record.comment && (
                    <div style={{ color: '#666', marginBottom: 8 }}>
                      审核意见：{record.comment}
                    </div>
                  )}
                  <div style={{ color: '#999', fontSize: 12 }}>
                    {dayjs(record.created_at).format('YYYY-MM-DD HH:mm:ss')}
                  </div>
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        )}
      </Card>
    </PageContainer>
  );
};

export default AuditHistory;