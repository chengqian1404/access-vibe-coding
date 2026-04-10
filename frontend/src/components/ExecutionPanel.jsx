import React from 'react';
import { Card, Progress, Steps, Tag, Typography, Spin, Result, Button } from 'antd';
import {
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';

const { Text, Title } = Typography;

const STATUS_COLORS = {
  idle: 'default',
  parsing: 'processing',
  parsed: 'processing',
  executing: 'processing',
  success: 'success',
  error: 'error',
};

const STATUS_LABELS = {
  idle: '等待',
  parsing: '解析指令中...',
  parsed: '解析完成，准备执行',
  executing: '执行中...',
  success: '执行成功',
  error: '执行失败',
};

function ExecutionPanel({ status = 'idle', progress = 0, message = '', result = null, parsed = null, onRetry }) {
  if (status === 'idle') {
    return (
      <Card className="execution-panel idle">
        <div className="idle-hint">
          <Text type="secondary">⌨️ 在上方输入指令后点击"执行指令"开始</Text>
        </div>
      </Card>
    );
  }

  const isLoading = ['parsing', 'parsed', 'executing'].includes(status);
  const isSuccess = status === 'success';
  const isError = status === 'error';

  return (
    <Card
      className={`execution-panel ${status}`}
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {isLoading && <Spin indicator={<LoadingOutlined spin />} size="small" />}
          {isSuccess && <CheckCircleOutlined style={{ color: '#52c41a' }} />}
          {isError && <CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
          <Text strong>{STATUS_LABELS[status] || status}</Text>
        </div>
      }
    >
      {/* Progress bar */}
      {isLoading && (
        <Progress
          percent={progress}
          status="active"
          strokeColor={{ from: '#108ee9', to: '#87d068' }}
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Current message */}
      {message && (
        <div className="execution-message">
          <Text>{message}</Text>
        </div>
      )}

      {/* Parsed instruction info */}
      {parsed && (
        <div className="parsed-info" style={{ marginTop: 12 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>识别的操作类型：</Text>
          <Tag color="blue" style={{ marginLeft: 8 }}>{parsed.action}</Tag>
          {parsed.confidence && (
            <Tag color={parsed.confidence > 0.8 ? 'green' : 'orange'}>
              置信度 {(parsed.confidence * 100).toFixed(0)}%
            </Tag>
          )}
          {parsed.description && (
            <div style={{ marginTop: 8 }}>
              <Text style={{ fontSize: 13 }}>{parsed.description}</Text>
            </div>
          )}
          {parsed.warnings && parsed.warnings.length > 0 && (
            <div style={{ marginTop: 8 }}>
              {parsed.warnings.map((w, i) => (
                <Tag key={i} color="warning">⚠️ {w}</Tag>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Result */}
      {isSuccess && result && (
        <div className="execution-result success">
          <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
          <Text>
            执行完成！共 {result.total_steps} 步，
            耗时 {result.execution_time?.toFixed(2)} 秒
          </Text>
        </div>
      )}

      {isError && (
        <div className="execution-result error">
          <CloseCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
          <Text type="danger">{result?.error || '执行失败，请重试'}</Text>
          {onRetry && (
            <Button type="link" size="small" onClick={onRetry} style={{ marginLeft: 8 }}>
              重试
            </Button>
          )}
        </div>
      )}
    </Card>
  );
}

export default ExecutionPanel;
