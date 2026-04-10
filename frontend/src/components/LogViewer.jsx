import React, { useState, useRef, useEffect } from 'react';
import { Card, Typography, Button, Switch, Tag, Empty } from 'antd';
import { ClearOutlined, DownloadOutlined } from '@ant-design/icons';

const { Text } = Typography;

const LOG_COLORS = {
  info: { color: '#1677ff', bg: '#e6f4ff' },
  success: { color: '#52c41a', bg: '#f6ffed' },
  warning: { color: '#faad14', bg: '#fffbe6' },
  error: { color: '#ff4d4f', bg: '#fff2f0' },
  debug: { color: '#8c8c8c', bg: '#fafafa' },
};

function LogViewer({ logs = [], onClear }) {
  const [autoScroll, setAutoScroll] = useState(true);
  const logEndRef = useRef(null);

  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const handleDownload = () => {
    const content = logs.map(log =>
      `[${log.time}] [${log.level?.toUpperCase()}] ${log.message}`
    ).join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `access-vibe-coding-log-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Card
      className="log-viewer"
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Text strong>📋 执行日志</Text>
          <Tag color="blue">{logs.length} 条</Tag>
        </div>
      }
      extra={
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>自动滚动</Text>
            <Switch size="small" checked={autoScroll} onChange={setAutoScroll} />
          </div>
          <Button size="small" icon={<DownloadOutlined />} onClick={handleDownload} disabled={!logs.length}>
            导出
          </Button>
          <Button size="small" icon={<ClearOutlined />} onClick={onClear} disabled={!logs.length}>
            清空
          </Button>
        </div>
      }
      bodyStyle={{ padding: 0 }}
    >
      <div className="log-container" style={{ height: 250, overflowY: 'auto', padding: '8px 0' }}>
        {logs.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无日志"
            style={{ margin: '20px 0' }}
          />
        ) : (
          logs.map((log, i) => {
            const colorConfig = LOG_COLORS[log.level] || LOG_COLORS.info;
            return (
              <div key={i} className="log-entry" style={{ padding: '2px 12px' }}>
                <span style={{ color: '#8c8c8c', fontSize: 11, marginRight: 8, fontFamily: 'monospace' }}>
                  {log.time}
                </span>
                <Tag
                  style={{
                    color: colorConfig.color,
                    backgroundColor: colorConfig.bg,
                    border: 'none',
                    marginRight: 6,
                    fontSize: 11,
                    lineHeight: '18px',
                  }}
                >
                  {(log.level || 'info').toUpperCase()}
                </Tag>
                <Text style={{ fontSize: 13 }}>{log.message}</Text>
              </div>
            );
          })
        )}
        <div ref={logEndRef} />
      </div>
    </Card>
  );
}

export default LogViewer;
