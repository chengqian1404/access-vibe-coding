import React, { useState, useEffect } from 'react';
import { Typography, Space, Divider, Form, Select, Slider, Switch, Card, message } from 'antd';
import LLMConfig from '../components/LLMConfig';
import axios from 'axios';
import { getBackendUrl } from '../config';

const { Title, Text } = Typography;
const { Option } = Select;

function Settings() {
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const baseUrl = await getBackendUrl();
      const res = await axios.get(`${baseUrl}/api/v1/config`);
      setConfig(res.data.config || {});
    } catch (err) {
      console.error('Failed to load config:', err);
    }
  };

  const handleSetDefaultProvider = async (provider) => {
    try {
      const baseUrl = await getBackendUrl();
      await axios.post(`${baseUrl}/api/v1/config/default-provider?provider=${provider}`);
      message.success(`已设置默认提供商: ${provider}`);
      await loadConfig();
    } catch (err) {
      message.error('设置失败');
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>⚙️ 设置</Title>
      </div>

      <Space direction="vertical" style={{ width: '100%' }} size={16}>
        {/* LLM Configuration */}
        <LLMConfig onConfigSaved={loadConfig} />

        {/* Default Provider */}
        <Card title={<Title level={5} style={{ margin: 0 }}>🎯 默认 LLM 提供商</Title>}>
          <Form layout="vertical">
            <Form.Item label="选择默认提供商" extra="执行指令时默认使用此提供商">
              <Select
                value={config.default_provider}
                onChange={handleSetDefaultProvider}
                style={{ maxWidth: 300 }}
              >
                {Object.entries(config.providers || {}).map(([id, cfg]) => (
                  <Option key={id} value={id}>
                    {id}
                    {cfg.api_key_set && ' ✓'}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Form>
        </Card>

        {/* About */}
        <Card title={<Title level={5} style={{ margin: 0 }}>ℹ️ 关于</Title>}>
          <Space direction="vertical">
            <Text><strong>Access Vibe Coding</strong></Text>
            <Text type="secondary">版本: 1.0.0</Text>
            <Text type="secondary">
              AI 驱动的 Microsoft Access 自动化工具，通过自然语言指令自动操作 Access 数据库。
            </Text>
            <Divider />
            <Text type="secondary">支持的 LLM 提供商: OpenAI、通义千问、Claude、DeepSeek、Ollama</Text>
          </Space>
        </Card>
      </Space>
    </div>
  );
}

export default Settings;
