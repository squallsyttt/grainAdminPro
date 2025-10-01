/**
 * 合同上传页面
 *
 * 功能：
 * - 文件上传组件（支持图片和PDF）
 * - 上传前预览
 * - 上传历史列表
 */
import React, { useState } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Card, Upload, Button, message, List, Image } from 'antd';
import { UploadOutlined, FileImageOutlined, FilePdfOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import dayjs from 'dayjs';
import { uploadFile } from '@/services/file';
import type { FileInfo } from '@/services/file';

/**
 * 合同上传页面
 */
const ContractUpload: React.FC = () => {
  const [fileList, setFileList] = useState<any[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<FileInfo[]>([]);
  const [uploading, setUploading] = useState(false);

  /**
   * 上传前验证
   */
  const beforeUpload = (file: File) => {
    const isJpgOrPngOrPdf =
      file.type === 'image/jpeg' ||
      file.type === 'image/png' ||
      file.type === 'application/pdf';

    if (!isJpgOrPngOrPdf) {
      message.error('只能上传 JPG/PNG/PDF 格式的文件！');
      return false;
    }

    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('文件大小不能超过 10MB！');
      return false;
    }

    return true;
  };

  /**
   * 文件上传
   */
  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件');
      return;
    }

    setUploading(true);

    try {
      // 逐个上传文件
      for (const fileItem of fileList) {
        const response = await uploadFile(fileItem.originFileObj, 'contract');
        setUploadedFiles((prev) => [...prev, response.data]);
      }

      message.success('上传成功！');
      setFileList([]);
    } catch (error) {
      message.error('上传失败，请重试');
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  /**
   * Upload组件配置
   */
  const uploadProps: UploadProps = {
    onRemove: (file) => {
      const index = fileList.indexOf(file);
      const newFileList = fileList.slice();
      newFileList.splice(index, 1);
      setFileList(newFileList);
    },
    beforeUpload: (file) => {
      if (beforeUpload(file)) {
        setFileList((prev) => [...prev, file]);
      }
      return false; // 阻止自动上传
    },
    fileList,
    listType: 'picture-card',
    accept: 'image/jpeg,image/png,application/pdf',
  };

  /**
   * 获取文件图标
   */
  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) {
      return <FilePdfOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />;
    }
    return <FileImageOutlined style={{ fontSize: 24, color: '#1890ff' }} />;
  };

  return (
    <PageContainer
      title="合同上传"
      content="请上传线下签署的合同照片或扫描件，支持JPG、PNG、PDF格式，单个文件不超过10MB"
    >
      {/* 文件上传区域 */}
      <Card title="上传合同文件" bordered={false} style={{ marginBottom: 24 }}>
        <Upload {...uploadProps}>
          <div>
            <UploadOutlined />
            <div style={{ marginTop: 8 }}>选择文件</div>
          </div>
        </Upload>
        <Button
          type="primary"
          onClick={handleUpload}
          disabled={fileList.length === 0}
          loading={uploading}
          style={{ marginTop: 16 }}
        >
          {uploading ? '上传中...' : '开始上传'}
        </Button>
      </Card>

      {/* 上传历史列表 */}
      <Card title="上传历史" bordered={false}>
        {uploadedFiles.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
            暂无上传记录
          </div>
        ) : (
          <List
            itemLayout="horizontal"
            dataSource={uploadedFiles}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  avatar={getFileIcon(item.file_type)}
                  title={item.file_path.split('/').pop()}
                  description={`上传时间：${dayjs(item.uploaded_at).format(
                    'YYYY-MM-DD HH:mm:ss'
                  )} | 文件大小：${(item.file_size / 1024).toFixed(2)} KB`}
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </PageContainer>
  );
};

export default ContractUpload;