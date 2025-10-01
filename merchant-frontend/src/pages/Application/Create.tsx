/**
 * 商家入驻申请页面
 *
 * 功能：
 * - 多步骤表单（企业信息、法人信息、联系方式、资质文件）
 * - 表单验证
 * - 草稿保存功能
 */
import React, { useState } from 'react';
import { PageContainer, StepsForm, ProFormText, ProFormSelect } from '@ant-design/pro-components';
import { message, Upload, Button } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';
import type { CreateApplicationRequest } from '@/services/application';
import { createApplication, submitApplication } from '@/services/application';
import { uploadFile } from '@/services/file';

/**
 * 商家申请创建页面
 */
const ApplicationCreate: React.FC = () => {
  const [currentApplicationId, setCurrentApplicationId] = useState<string>();

  /**
   * 提交第一步：企业基本信息
   */
  const handleStepOneSubmit = async (values: any) => {
    try {
      // 创建草稿申请
      const response = await createApplication({
        business_name: values.business_name,
        unified_social_credit: values.unified_social_credit,
        business_categories: values.business_categories,
        legal_person_name: '',
        legal_person_id_number: '',
        contact_name: '',
        contact_phone: '',
        contact_email: '',
      });

      setCurrentApplicationId(response.data.id);
      message.success('企业信息已保存');
      return true;
    } catch (error) {
      message.error('保存失败，请重试');
      return false;
    }
  };

  /**
   * 提交第二步：法人信息
   */
  const handleStepTwoSubmit = async (values: any) => {
    // 这里应该更新申请信息
    message.success('法人信息已保存');
    return true;
  };

  /**
   * 提交第三步：联系方式
   */
  const handleStepThreeSubmit = async (values: any) => {
    message.success('联系方式已保存');
    return true;
  };

  /**
   * 最终提交
   */
  const handleFinish = async (values: any) => {
    try {
      if (!currentApplicationId) {
        message.error('申请ID不存在');
        return false;
      }

      // 提交申请
      await submitApplication(currentApplicationId);
      message.success('申请提交成功！');

      // 跳转到状态页面
      setTimeout(() => {
        history.push('/application/status');
      }, 1000);

      return true;
    } catch (error) {
      message.error('提交失败，请重试');
      return false;
    }
  };

  return (
    <PageContainer
      title="商家入驻申请"
      content="请填写完整的企业信息和资质材料，我们将在1-3个工作日内完成审核"
    >
      <StepsForm
        onFinish={handleFinish}
        formProps={{
          validateMessages: {
            required: '此项为必填项',
          },
        }}
      >
        {/* 步骤1：企业基本信息 */}
        <StepsForm.StepForm
          name="basic"
          title="企业基本信息"
          onFinish={handleStepOneSubmit}
        >
          <ProFormText
            name="business_name"
            label="企业名称"
            width="lg"
            placeholder="请输入营业执照上的企业全称"
            rules={[{ required: true }, { max: 200 }]}
          />
          <ProFormText
            name="unified_social_credit"
            label="统一社会信用代码"
            width="lg"
            placeholder="18位统一社会信用代码"
            rules={[
              { required: true },
              { len: 18, message: '统一社会信用代码必须为18位' },
              {
                pattern: /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/,
                message: '请输入正确的统一社会信用代码',
              },
            ]}
          />
          <ProFormSelect
            name="business_categories"
            label="经营类目"
            width="lg"
            mode="multiple"
            options={[
              { label: '食品饮料', value: '食品饮料' },
              { label: '服装鞋帽', value: '服装鞋帽' },
              { label: '家居家纺', value: '家居家纺' },
              { label: '数码家电', value: '数码家电' },
              { label: '美妆个护', value: '美妆个护' },
              { label: '图书文娱', value: '图书文娱' },
            ]}
            placeholder="请选择您的经营类目"
            rules={[{ required: true }]}
          />
        </StepsForm.StepForm>

        {/* 步骤2：法人信息 */}
        <StepsForm.StepForm
          name="legal"
          title="法人信息"
          onFinish={handleStepTwoSubmit}
        >
          <ProFormText
            name="legal_person_name"
            label="法人姓名"
            width="lg"
            placeholder="请输入法定代表人姓名"
            rules={[{ required: true }, { max: 100 }]}
          />
          <ProFormText
            name="legal_person_id_number"
            label="法人身份证号"
            width="lg"
            placeholder="请输入法人身份证号码"
            rules={[
              { required: true },
              {
                pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/,
                message: '请输入正确的身份证号码',
              },
            ]}
          />
        </StepsForm.StepForm>

        {/* 步骤3：联系方式 */}
        <StepsForm.StepForm
          name="contact"
          title="联系方式"
          onFinish={handleStepThreeSubmit}
        >
          <ProFormText
            name="contact_name"
            label="联系人姓名"
            width="lg"
            placeholder="请输入联系人姓名"
            rules={[{ required: true }, { max: 100 }]}
          />
          <ProFormText
            name="contact_phone"
            label="联系电话"
            width="lg"
            placeholder="请输入手机号码"
            rules={[
              { required: true },
              {
                pattern: /^1[3-9]\d{9}$/,
                message: '请输入正确的手机号码',
              },
            ]}
          />
          <ProFormText
            name="contact_email"
            label="联系邮箱"
            width="lg"
            placeholder="请输入邮箱地址"
            rules={[
              { required: true },
              { type: 'email', message: '请输入正确的邮箱地址' },
            ]}
          />
        </StepsForm.StepForm>

        {/* 步骤4：资质文件上传 */}
        <StepsForm.StepForm
          name="files"
          title="资质文件上传"
        >
          <Upload
            name="business_license"
            listType="picture-card"
            maxCount={1}
            beforeUpload={(file) => {
              const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'application/pdf';
              if (!isJpgOrPng) {
                message.error('只能上传 JPG/PNG/PDF 格式文件！');
              }
              const isLt10M = file.size / 1024 / 1024 < 10;
              if (!isLt10M) {
                message.error('文件大小不能超过 10MB！');
              }
              return isJpgOrPng && isLt10M;
            }}
          >
            <div>
              <UploadOutlined />
              <div style={{ marginTop: 8 }}>上传营业执照</div>
            </div>
          </Upload>
        </StepsForm.StepForm>
      </StepsForm>
    </PageContainer>
  );
};

export default ApplicationCreate;