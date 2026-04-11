import React, { useState, useEffect, useRef, useContext } from 'react';
import { Card, Button, Select, Space, Typography, Tag } from 'antd';
import { ClearOutlined } from '@ant-design/icons';
import { AppContext } from '../App';

const { Text } = Typography;
const { Option } = Select;

const levelColors = {
  info: 'blue',
  warn: 'orange',
  warning: 'orange',
  error: 'red',
  debug: 'default',
  success: 'green'
};

const levelLabels = {
  info: 'INFO',
  warn: 'WARN',
  warning: 'WARN',
  error: 'ERROR',
  debug: 'DEBUG',
  success: 'OK'
};

function LogViewer() {
  const { logs } = useContext(AppContext);
  const [filter, setFilter] = useState('all');
  const [clearedAt, setClearedAt] = useState(0);
  const bottomRef = useRef(null);

  const visibleLogs = logs.slice(clearedAt);
  const filtered =
    filter === 'all'
      ? visibleLogs
      : visibleLogs.filter((l) => {
          if (filter === 'warn') return l.level === 'warn' || l.level === 'warning';
          return l.level === filter;
        });

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filtered.length]);

  const formatTime = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`;
  };

  return (
    <Card
      title="运行日志"
      size="small"
      extra={
        <Space>
          <Select value={filter} onChange={setFilter} size="small" style={{ width: 90 }}>
            <Option value="all">全部</Option>
            <Option value="info">INFO</Option>
            <Option value="warn">WARN</Option>
            <Option value="error">ERROR</Option>
          </Select>
          <Button
            size="small"
            icon={<ClearOutlined />}
            onClick={() => setClearedAt(logs.length)}
          >
            清空
          </Button>
        </Space>
      }
    >
      <div
        className="log-viewer"
        style={{ height: 200, overflowY: 'auto', fontFamily: 'monospace', fontSize: 12 }}
      >
        {filtered.map((log, i) => (
          <div
            key={log.id || i}
            style={{ padding: '1px 0', borderBottom: '1px solid #f0f0f0' }}
          >
            <Text type="secondary" style={{ marginRight: 8 }}>
              {formatTime(log.time)}
            </Text>
            <Tag
              color={levelColors[log.level] || 'default'}
              style={{ fontSize: 10, padding: '0 4px', lineHeight: '16px', marginRight: 8 }}
            >
              {levelLabels[log.level] || (log.level && log.level.toUpperCase()) || 'INFO'}
            </Tag>
            <Text>{log.message}</Text>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </Card>
  );
}

export default LogViewer;
