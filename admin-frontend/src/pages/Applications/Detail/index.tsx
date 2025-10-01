/**
 * 申请审核页面
 *
 * 功能：
 * - 显示申请详细信息
 * - 预览上传的资质文件
 * - 审核操作（通过/拒绝/要求补充材料）
 */
import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Card, Button, Modal, Form, Input, message, Space, Spin } from 'antd';
import { CheckOutlined, CloseOutlined, ExclamationCircleOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { history, useParams } from '@umijs/max';
import ApplicationDetail from '@/components/ApplicationDetail';
import type { Application } from '@/services/application';
import { getApplication, ApplicationStatus } from '@/services/application';
import { createAudit, AuditAction, AuditResult } from '@/services/audit';

/**
 * 申请审核页面
 */
const ApplicationAudit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [application, setApplication] = useState<Application | null>(null);
  const [loading, setLoading] = useState(false);
  const [auditModalVisible, setAuditModalVisible] = useState(false);
  const [auditAction, setAuditAction] = useState<AuditAction>(AuditAction.APPROVE);
  const [form] = Form.useForm();

  /**
   * 获取申请详情
   */
  const loadApplication = useCallback(async () => {
    if (!id) return;

    setLoading(true);
    try {
      const response = await getApplication(id);
      setApplication(response.data);
    } catch (error) {
      message.error('加载申请详情失败');
      console.error('Failed to load application:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  /**
   * 加载申请详情
   */
  useEffect(() => {
    if (id) {
      loadApplication();
    }
  }, [id, loadApplication]);

  /**
   * 打开审核Modal
   */
  const openAuditModal = (action: AuditAction) => {
    setAuditAction(action);
    setAuditModalVisible(true);
    form.resetFields();
  };

  /**
   * 提交审核
   */
  const handleAuditSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (!application) return;

      setLoading(true);

      // 根据操作确定结果
      let result: AuditResult;
      switch (auditAction) {
        case AuditAction.APPROVE:
          result = AuditResult.APPROVED;
          break;
        case AuditAction.REJECT:
          result = AuditResult.REJECTED;
          break;
        case AuditAction.REQUEST_SUPPLEMENT:
          result = AuditResult.PENDING_SUPPLEMENT;
          break;
        default:
          result = AuditResult.IN_PROGRESS;
      }

      await createAudit({
        application_id: application.id,
        action: auditAction,
        result,
        comment: values.comment,
      });

      message.success('审核操作成功');
      setAuditModalVisible(false);

      // 返回列表页
      setTimeout(() => {
        history.push('/applications/list');
      }, 1000);
    } catch (error) {
      message.error('审核操作失败');
      console.error('Failed to submit audit:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 获取审核操作文本
   */
  const getAuditActionText = (action: AuditAction): string => {
    switch (action) {
      case AuditAction.APPROVE:
        return '通过';
      case AuditAction.REJECT:
        return '拒绝';
      case AuditAction.REQUEST_SUPPLEMENT:
        return '要求补充材料';
      default:
        return '';
    }
  };

  /**
   * 判断是否需要填写审核意见
   */
  const isCommentRequired = (action: AuditAction): boolean => {
    return action === AuditAction.REJECT || action === AuditAction.REQUEST_SUPPLEMENT;
  };

  /**
   * 判断是否可以审核
   */
  const canAudit = (): boolean => {
    if (!application) return false;
    return (
      application.status === ApplicationStatus.PENDING ||
      application.status === ApplicationStatus.UNDER_REVIEW
    );
  };

  if (loading && !application) {
    return (
      <PageContainer>
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
      <PageContainer>
        <Card>
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            申请信息不存在
          </div>
        </Card>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title="申请审核"
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
      {/* 申请详情 */}
      <ApplicationDetail application={application} />

      {/* 审核操作按钮 */}
      {canAudit() && (
        <Card
          title="审核操作"
          bordered={false}
          style={{ marginTop: 24 }}
        >
          <Space size="large">
            <Button
              type="primary"
              icon={<CheckOutlined />}
              size="large"
              onClick={() => openAuditModal(AuditAction.APPROVE)}
              loading={loading}
            >
              审核通过
            </Button>
            <Button
              danger
              icon={<CloseOutlined />}
              size="large"
              onClick={() => openAuditModal(AuditAction.REJECT)}
              loading={loading}
            >
              审核拒绝
            </Button>
            <Button
              icon={<ExclamationCircleOutlined />}
              size="large"
              onClick={() => openAuditModal(AuditAction.REQUEST_SUPPLEMENT)}
              loading={loading}
            >
              要求补充材料
            </Button>
          </Space>
        </Card>
      )}

      {/* 审核意见Modal */}
      <Modal
        title={`${getAuditActionText(auditAction)}申请`}
        open={auditModalVisible}
        onOk={handleAuditSubmit}
        onCancel={() => setAuditModalVisible(false)}
        confirmLoading={loading}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          preserve={false}
        >
          <Form.Item
            name="comment"
            label="审核意见"
            rules={[
              {
                required: isCommentRequired(auditAction),
                message: '请输入审核意见',
              },
              {
                max: 500,
                message: '审核意见不能超过500个字符',
              },
            ]}
          >
            <Input.TextArea
              rows={4}
              placeholder={
                isCommentRequired(auditAction)
                  ? '请输入审核意见（必填）'
                  : '请输入审核意见（选填）'
              }
            />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default ApplicationAudit;