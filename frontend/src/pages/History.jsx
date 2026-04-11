import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Button,
  Space,
  Typography,
  Statistic,
  Row,
  Col,
  Input,
  Popconfirm,
  Tag,
  notification
} from 'antd';
import {
  DeleteOutlined,
  BarChartOutlined,
  DownloadOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { getRecordings, deleteRecording, downloadReport } from '../utils/api';
import {
  formatDateTime,
  formatDuration,
  formatFileSize,
  getStatusColor,
  getStatusText
} from '../utils/helpers';

const { Title } = Typography;
const { Search } = Input;

function History() {
  const [recordings, setRecordings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const load = async () => {
    setLoading(true);
    try {
      const data = await getRecordings();
      const list = Array.isArray(data) ? data : data?.recordings || [];
      setRecordings(list);
      setPagination((p) => ({ ...p, total: list.length }));
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id) => {
    try {
      await deleteRecording(id);
      notification.success({ message: '删除成功' });
      load();
    } catch (e) {
      // error handled in api.js
    }
  };

  const handleDownload = (id) => {
    const url = downloadReport(id);
    window.open(url, '_blank');
  };

  const filtered = search
    ? recordings.filter((r) =>
        (r.title || r.id || '').toLowerCase().includes(search.toLowerCase())
      )
    : recordings;

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (v, r) => v || r.id || '--',
      ellipsis: true
    },
    {
      title: '日期',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (v) => formatDateTime(v)
    },
    {
      title: '时长',
      dataIndex: 'duration',
      key: 'duration',
      width: 90,
      render: (v) => formatDuration(v)
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (v) => formatFileSize(v)
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (v) => <Tag color={getStatusColor(v)}>{getStatusText(v)}</Tag>
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      render: (_, r) => (
        <Space>
          <Button
            size="small"
            icon={<BarChartOutlined />}
            type="link"
            onClick={() => {}}
          >
            分析
          </Button>
          <Button
            size="small"
            icon={<DownloadOutlined />}
            type="link"
            onClick={() => handleDownload(r.id)}
          >
            下载
          </Button>
          <Popconfirm
            title="确定删除？"
            onConfirm={() => handleDelete(r.id)}
            okText="删除"
            cancelText="取消"
          >
            <Button size="small" icon={<DeleteOutlined />} type="link" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const totalDuration = recordings.reduce((s, r) => s + (r.duration || 0), 0);
  const totalSize = recordings.reduce((s, r) => s + (r.file_size || 0), 0);

  return (
    <div className="history-page">
      <Title level={4} style={{ marginBottom: 16 }}>
        历史记录
      </Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总录制数" value={recordings.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="总时长" value={formatDuration(totalDuration)} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="总大小" value={formatFileSize(totalSize)} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已分析"
              value={
                recordings.filter(
                  (r) => r.status === 'completed' || r.analysis_status === 'done'
                ).length
              }
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <div
          style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between' }}
        >
          <Search
            placeholder="搜索录制"
            onSearch={setSearch}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 240 }}
          />
          <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>
            刷新
          </Button>
        </div>
        <Table
          dataSource={filtered}
          columns={columns}
          rowKey={(r) => r.id}
          loading={loading}
          pagination={pagination}
          onChange={(p) => setPagination(p)}
          size="small"
          locale={{ emptyText: '暂无录制记录' }}
        />
      </Card>
    </div>
  );
}

export default History;
