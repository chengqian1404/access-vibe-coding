import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Switch,
  Divider,
  Space,
  Typography,
  Row,
  Col,
  Popconfirm,
  notification
} from 'antd';
import {
  SaveOutlined,
  KeyOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone
} from '@ant-design/icons';
import { getConfig, updateConfig } from '../utils/api';
import storage, { KEYS } from '../utils/storage';

const { Title } = Typography;
const { Option } = Select;
const { Password } = Input;

const ALL_MODELS = [
  { value: 'qwen-turbo', label: 'qwen-turbo' },
  { value: 'qwen-plus', label: 'qwen-plus' },
  { value: 'qwen-max', label: 'qwen-max' },
  { value: 'qwen-long', label: 'qwen-long' },
  { value: 'gpt-4o', label: 'gpt-4o' },
  { value: 'gpt-4o-mini', label: 'gpt-4o-mini' },
  { value: 'gpt-4-turbo', label: 'gpt-4-turbo' },
  { value: 'gpt-3.5-turbo', label: 'gpt-3.5-turbo' },
  { value: 'claude-3-5-sonnet-20241022', label: 'claude-3-5-sonnet-20241022' },
  { value: 'claude-3-haiku-20240307', label: 'claude-3-haiku-20240307' },
  { value: 'claude-3-opus-20240229', label: 'claude-3-opus-20240229' },
  { value: 'deepseek-chat', label: 'deepseek-chat' },
  { value: 'deepseek-coder', label: 'deepseek-coder' }
];

function Settings() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    getConfig()
      .then((data) => {
        if (data) {
          form.setFieldsValue({
            llmProvider: data.llm_provider || storage.get(KEYS.LLM_PROVIDER, 'qwen'),
            llmApiKey: data.llm_api_key || storage.get(KEYS.LLM_API_KEY, ''),
            llmModel: data.llm_model || storage.get(KEYS.LLM_MODEL, 'qwen-turbo'),
            whisperApiKey: data.whisper_api_key || storage.get(KEYS.WHISPER_API_KEY, ''),
            whisperLanguage:
              data.whisper_language || storage.get(KEYS.WHISPER_LANGUAGE, 'auto'),
            defaultFps: data.default_fps || storage.get(KEYS.DEFAULT_FPS, 10),
            storagePath: data.storage_path || storage.get(KEYS.STORAGE_PATH, ''),
            autoStart: data.auto_start || false,
            language: 'zh',
            theme: storage.get(KEYS.THEME, 'light')
          });
        }
      })
      .catch(() => {
        form.setFieldsValue({
          llmProvider: storage.get(KEYS.LLM_PROVIDER, 'qwen'),
          llmApiKey: storage.get(KEYS.LLM_API_KEY, ''),
          llmModel: storage.get(KEYS.LLM_MODEL, 'qwen-turbo'),
          whisperApiKey: storage.get(KEYS.WHISPER_API_KEY, ''),
          whisperLanguage: storage.get(KEYS.WHISPER_LANGUAGE, 'auto'),
          defaultFps: storage.get(KEYS.DEFAULT_FPS, 10),
          storagePath: storage.get(KEYS.STORAGE_PATH, ''),
          autoStart: false,
          language: 'zh',
          theme: storage.get(KEYS.THEME, 'light')
        });
      });
  }, [form]);

  const handleSave = async (values) => {
    setLoading(true);
    try {
      storage.set(KEYS.LLM_PROVIDER, values.llmProvider);
      storage.set(KEYS.LLM_API_KEY, values.llmApiKey);
      storage.set(KEYS.LLM_MODEL, values.llmModel);
      storage.set(KEYS.WHISPER_API_KEY, values.whisperApiKey);
      storage.set(KEYS.WHISPER_LANGUAGE, values.whisperLanguage);
      storage.set(KEYS.DEFAULT_FPS, values.defaultFps);
      storage.set(KEYS.THEME, values.theme);
      if (values.storagePath) storage.set(KEYS.STORAGE_PATH, values.storagePath);

      await updateConfig({
        llm_provider: values.llmProvider,
        llm_api_key: values.llmApiKey,
        llm_model: values.llmModel,
        whisper_api_key: values.whisperApiKey,
        whisper_language: values.whisperLanguage,
        default_fps: values.defaultFps,
        storage_path: values.storagePath,
        auto_start: values.autoStart
      });
      notification.success({ message: '设置已保存' });
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    setTestLoading(true);
    try {
      const values = form.getFieldsValue();
      await updateConfig({
        llm_provider: values.llmProvider,
        llm_api_key: values.llmApiKey,
        llm_model: values.llmModel
      });
      notification.success({ message: 'API 连接测试成功！' });
    } catch (e) {
      notification.error({ message: 'API 连接测试失败' });
    } finally {
      setTestLoading(false);
    }
  };

  const handleClearData = () => {
    localStorage.clear();
    notification.success({ message: '数据已清除，请重启应用' });
    setTimeout(() => window.location.reload(), 1500);
  };

  return (
    <div className="settings-page">
      <Title level={4} style={{ marginBottom: 16 }}>
        系统设置
      </Title>
      <Form form={form} layout="vertical" onFinish={handleSave}>
        <Card title="大模型设置" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item label="LLM 提供商" name="llmProvider">
                <Select>
                  <Option value="qwen">通义千问 (Qwen)</Option>
                  <Option value="openai">OpenAI</Option>
                  <Option value="claude">Claude (Anthropic)</Option>
                  <Option value="deepseek">DeepSeek</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="模型" name="llmModel">
                <Select placeholder="选择模型">
                  {ALL_MODELS.map((m) => (
                    <Option key={m.value} value={m.value}>
                      {m.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="API Key" name="llmApiKey">
                <Password
                  placeholder="输入 API Key"
                  iconRender={(v) => (v ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>
            </Col>
          </Row>
          <Button onClick={handleTest} loading={testLoading} icon={<KeyOutlined />}>
            测试连接
          </Button>
        </Card>

        <Card title="Whisper 语音识别" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Whisper API Key" name="whisperApiKey">
                <Password
                  placeholder="输入 Whisper API Key (OpenAI)"
                  iconRender={(v) => (v ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="识别语言" name="whisperLanguage">
                <Select>
                  <Option value="auto">自动检测</Option>
                  <Option value="zh">中文</Option>
                  <Option value="en">英文</Option>
                  <Option value="ja">日文</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Card title="录制设置" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item label="默认帧率 (FPS)" name="defaultFps">
                <Select>
                  <Option value={5}>5 FPS</Option>
                  <Option value={10}>10 FPS</Option>
                  <Option value={15}>15 FPS</Option>
                  <Option value={24}>24 FPS</Option>
                  <Option value={30}>30 FPS</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={16}>
              <Form.Item label="存储路径" name="storagePath">
                <Input placeholder="留空使用默认路径" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Card title="应用设置" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item label="界面主题" name="theme">
                <Select>
                  <Option value="light">浅色</Option>
                  <Option value="dark">深色（开发中）</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="界面语言" name="language">
                <Select>
                  <Option value="zh">中文</Option>
                  <Option value="en">English</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="开机自启" name="autoStart" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          <Divider />
          <Popconfirm
            title="确定清除所有数据？"
            description="此操作将清除所有本地设置，无法恢复。"
            onConfirm={handleClearData}
            okText="确定清除"
            cancelText="取消"
            okType="danger"
          >
            <Button danger>清除所有数据</Button>
          </Popconfirm>
        </Card>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<SaveOutlined />}
            size="large"
          >
            保存设置
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default Settings;
