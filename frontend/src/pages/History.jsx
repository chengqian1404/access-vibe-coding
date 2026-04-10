import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography, Table, Tag, Button, Space, Popconfirm, message, Empty, Tooltip,
} from 'antd';
import { DeleteOutlined, ReloadOutlined, ClearOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import { getBackendUrl } from '../config';

const { Title, Text } = Typography;

const STATUS_COLORS = {
  success: 'success',
  failed: 'error',
  error: 'error',
  pending: 'processing',
};

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const baseUrl = await getBackendUrl();
      const res = await axios.get(`${baseUrl}/api/v1/history?limit=50`);
      setHistory(res.data.history || []);
    } catch (err) {
      message.error('加载历史记录失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleDelete = async (id) => {
    try {
      const baseUrl = await getBackendUrl();
      await axios.delete(`${baseUrl}/api/v1/history/${id}`);
      setHistory(prev => prev.filter(item => item.id !== id));
      message.success('已删除');
    } catch {
      message.error('删除失败');
    }
  };

  const handleClearAll = async () => {
    try {
      const baseUrl = await getBackendUrl();
      await axios.delete(`${baseUrl}/api/v1/history`);
      setHistory([]);
      message.success('已清空历史记录');
    } catch {
      message.error('清空失败');
    }
  };

  const columns = [
    {
      title: '时间',
      dataIndex: 'created_at',
      width: 160,
      render: (val) => (
        <Text style={{ fontSize: 12 }}>
          {dayjs(val).format('MM-DD HH:mm:ss')}
        </Text>
      ),
    },
    {
      title: '指令',
      dataIndex: 'instruction',
      ellipsis: true,
      render: (val) => (
        <Tooltip title={val}>
          <Text style={{ fontSize: 13 }}>{val}</Text>
        </Tooltip>
      ),
    },
    {
      title: '操作类型',
      dataIndex: 'parsed_action',
      width: 130,
      render: (val) => <Tag color="blue">{val}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (val) => (
        <Tag color={STATUS_COLORS[val] || 'default'}>
          {val === 'success' ? '成功' : val === 'failed' || val === 'error' ? '失败' : val}
        </Tag>
      ),
    },
    {
      title: '耗时',
      dataIndex: 'execution_time',
      width: 90,
      render: (val) => val ? <Text style={{ fontSize: 12 }}>{val.toFixed(2)}s</Text> : '-',
    },
    {
      title: '操作',
      width: 100,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="重新执行">
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              size="small"
              onClick={() => navigate('/', { state: { instruction: record.instruction } })}
            />
          </Tooltip>
          <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button type="text" icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>📋 历史记录</Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadHistory} loading={loading}>
            刷新
          </Button>
          <Popconfirm title="确定清空所有历史记录?" onConfirm={handleClearAll} okText="确定" cancelText="取消">
            <Button icon={<ClearOutlined />} danger disabled={!history.length}>
              清空
            </Button>
          </Popconfirm>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={history}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20, showTotal: (total) => `共 ${total} 条` }}
        locale={{ emptyText: <Empty description="暂无历史记录" /> }}
        size="middle"
      />
    </div>
  );
}

export default History;
