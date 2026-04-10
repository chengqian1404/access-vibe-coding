import React, { useState, useEffect } from 'react';
import {
  Card, Form, Select, Input, Button, Space, Typography, Alert, Divider, Tag, Spin,
  message as antMessage,
} from 'antd';
import { SaveOutlined, ApiOutlined, DeleteOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';
import axios from 'axios';
import { getBackendUrl } from '../config';

const { Option } = Select;
const { Text, Title } = Typography;

function LLMConfig({ onConfigSaved }) {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [currentConfig, setCurrentConfig] = useState({});
  const [form] = Form.useForm();

  useEffect(() => {
    loadProviders();
    loadCurrentConfig();
  }, []);

  const loadProviders = async () => {
    try {
      const baseUrl = await getBackendUrl();
      const res = await axios.get(`${baseUrl}/api/v1/providers`);
      setProviders(res.data.providers || []);
    } catch (err) {
      console.error('Failed to load providers:', err);
    }
  };

  const loadCurrentConfig = async () => {
    try {
      const baseUrl = await getBackendUrl();
      const res = await axios.get(`${baseUrl}/api/v1/config`);
      setCurrentConfig(res.data.config || {});
    } catch (err) {
      console.error('Failed to load config:', err);
    }
  };

  const handleProviderChange = (provider) => {
    setSelectedProvider(provider);
    form.resetFields(['api_key', 'base_url', 'model']);
  };

  const selectedProviderInfo = providers.find(p => p.id === selectedProvider);
  const savedConfig = currentConfig.providers?.[selectedProvider];

  const handleSave = async (values) => {
    setLoading(true);
    try {
      const baseUrl = await getBackendUrl();
      await axios.post(`${baseUrl}/api/v1/config/provider`, {
        provider: selectedProvider,
        api_key: values.api_key,
        base_url: values.base_url || null,
        model: values.model || null,
      });
      antMessage.success(`已保存 ${selectedProvider} 配置`);
      await loadCurrentConfig();
      if (onConfigSaved) onConfigSaved();
    } catch (err) {
      antMessage.error('保存失败：' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    const values = form.getFieldsValue();
    if (!values.api_key) {
      antMessage.warning('请先输入 API 密钥');
      return;
    }
    setTesting(true);
    try {
      const baseUrl = await getBackendUrl();
      const res = await axios.post(`${baseUrl}/api/v1/config/provider/test`, {
        provider: selectedProvider,
        api_key: values.api_key,
        model: values.model || null,
      });
      if (res.data.success) {
        antMessage.success('连接测试成功！');
      } else {
        antMessage.error(res.data.message || '连接测试失败');
      }
    } catch (err) {
      antMessage.error('连接测试失败：' + (err.response?.data?.detail || err.message));
    } finally {
      setTesting(false);
    }
  };

  const handleDelete = async () => {
    try {
      const baseUrl = await getBackendUrl();
      await axios.delete(`${baseUrl}/api/v1/config/provider/${selectedProvider}`);
      antMessage.success(`已删除 ${selectedProvider} 配置`);
      await loadCurrentConfig();
    } catch (err) {
      antMessage.error('删除失败');
    }
  };

  return (
    <Card className="llm-config" title={<Title level={5} style={{ margin: 0 }}>🤖 LLM 提供商配置</Title>}>
      <Form form={form} layout="vertical" onFinish={handleSave}>
        <Form.Item label="选择提供商" required>
          <Select value={selectedProvider} onChange={handleProviderChange} style={{ width: '100%' }}>
            {providers.map(p => (
              <Option key={p.id} value={p.id}>
                {p.name_zh || p.name}
                {savedConfig && currentConfig.providers?.[p.id]?.api_key_set && (
                  <Tag color="green" style={{ marginLeft: 8, fontSize: 11 }}>已配置</Tag>
                )}
              </Option>
            ))}
          </Select>
        </Form.Item>

        {selectedProviderInfo && (
          <>
            {selectedProviderInfo.requires_key && (
              <Form.Item
                label="API 密钥"
                name="api_key"
                rules={[{ required: true, message: '请输入 API 密钥' }]}
                extra={savedConfig?.api_key_set ? <Tag color="green">已有保存的密钥</Tag> : null}
              >
                <Input.Password
                  placeholder={savedConfig?.api_key_set ? '已保存（留空保持不变）' : '请输入 API 密钥'}
                  iconRender={visible => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>
            )}

            <Form.Item label="模型" name="model">
              <Select
                placeholder={`默认: ${selectedProviderInfo.default_model}`}
                allowClear
              >
                {selectedProviderInfo.models?.map(m => (
                  <Option key={m.id} value={m.id}>{m.name}</Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item label="自定义 API URL（可选）" name="base_url">
              <Input placeholder="留空使用默认地址" />
            </Form.Item>

            <Divider />

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                >
                  保存配置
                </Button>
                <Button
                  icon={<ApiOutlined />}
                  onClick={handleTest}
                  loading={testing}
                >
                  测试连接
                </Button>
                {savedConfig?.api_key_set && (
                  <Button
                    danger
                    icon={<DeleteOutlined />}
                    onClick={handleDelete}
                  >
                    删除配置
                  </Button>
                )}
              </Space>
            </Form.Item>
          </>
        )}
      </Form>

      {providers.length === 0 && (
        <Alert
          message="正在加载提供商列表..."
          type="info"
          showIcon
        />
      )}
    </Card>
  );
}

export default LLMConfig;
