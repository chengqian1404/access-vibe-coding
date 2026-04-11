import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Typography,
  Space,
  Alert,
  Steps
} from 'antd';
import {
  UserOutlined,
  WechatOutlined,
  CheckCircleOutlined,
  ArrowRightOutlined
} from '@ant-design/icons';
import storage, { KEYS } from '../utils/storage';
import { startMonitor } from '../utils/api';

const { Title, Text } = Typography;

function AccountSetup({ onComplete }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [tested, setTested] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async (values) => {
    setLoading(true);
    setError('');
    try {
      storage.set(KEYS.WEIXIN_ID, values.weixinId.trim());
      if (onComplete) onComplete();
    } catch (e) {
      setError(e.message || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    const id = form.getFieldValue('weixinId');
    if (!id || !id.trim()) {
      setError('请先输入视频号ID');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await startMonitor(id.trim());
      setTested(true);
    } catch (e) {
      setError('连接测试失败，请检查后端是否启动');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="account-setup-page"
    >
      <Card style={{ width: 520, boxShadow: '0 4px 24px rgba(0,0,0,0.10)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <WechatOutlined style={{ fontSize: 48, color: '#07c160', marginBottom: 8 }} />
          <Title level={3} style={{ marginBottom: 4 }}>
            直播学习分析工具
          </Title>
          <Text type="secondary">智能分析微信视频号直播内容</Text>
        </div>

        <Steps
          size="small"
          style={{ marginBottom: 24 }}
          items={[
            { title: '输入账号', icon: <UserOutlined /> },
            { title: '连接验证', icon: <CheckCircleOutlined /> },
            { title: '开始使用', icon: <ArrowRightOutlined /> }
          ]}
          current={tested ? 1 : 0}
        />

        <Alert
          message="使用说明"
          description="本工具可以自动监控微信视频号直播，录制直播内容并进行 AI 分析，生成问答对、文字记录和风格分析报告。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
            closable
            onClose={() => setError('')}
          />
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={{ weixinId: storage.get(KEYS.WEIXIN_ID, '') }}
        >
          <Form.Item
            label="微信视频号ID"
            name="weixinId"
            rules={[{ required: true, message: '请输入视频号ID' }]}
            extra={
              <Space direction="vertical" size={2} style={{ marginTop: 4 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  在微信中打开视频号主页，点击"..."可查看视频号ID
                </Text>
                <Button
                  type="link"
                  size="small"
                  style={{ padding: 0, height: 'auto' }}
                  onClick={() => {
                    if (window.electron?.openExternal) {
                      window.electron.openExternal('https://channels.weixin.qq.com');
                    }
                  }}
                >
                  打开微信视频号官网 →
                </Button>
              </Space>
            }
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="输入视频号ID，如: gh_xxxxxxxx"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%' }} direction="vertical">
              <Button
                type="default"
                block
                onClick={handleTest}
                loading={loading}
                icon={<WechatOutlined />}
              >
                测试连接
              </Button>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
                size="large"
                icon={<ArrowRightOutlined />}
              >
                保存并开始使用
              </Button>
            </Space>
          </Form.Item>
        </Form>

        {tested && (
          <Alert message="连接测试成功！" type="success" showIcon />
        )}
      </Card>
    </div>
  );
}

export default AccountSetup;
