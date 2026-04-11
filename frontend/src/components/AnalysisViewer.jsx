import React, { useState } from 'react';
import {
  Tabs,
  Table,
  Input,
  Button,
  Space,
  Typography,
  Tag,
  Row,
  Col,
  Statistic,
  List,
  Empty,
  Progress,
  Card
} from 'antd';
import {
  FileTextOutlined,
  FileExcelOutlined
} from '@ant-design/icons';
import { downloadReport } from '../utils/api';
import { formatDuration } from '../utils/helpers';

const { Text, Paragraph } = Typography;
const { Search } = Input;

function OverviewTab({ analysis }) {
  if (!analysis) return <Empty description="暂无分析数据" />;
  const s = analysis.summary || {};
  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Statistic title="总时长" value={formatDuration(s.duration)} />
        </Col>
        <Col span={6}>
          <Statistic title="问答对数" value={s.qa_count || 0} />
        </Col>
        <Col span={6}>
          <Statistic title="弹幕数量" value={s.danmaku_count || 0} />
        </Col>
        <Col span={6}>
          <Statistic title="发言次数" value={s.speech_count || 0} />
        </Col>
      </Row>
      {s.overview && (
        <Card size="small" title="内容概述">
          <Paragraph>{s.overview}</Paragraph>
        </Card>
      )}
      {s.topics && s.topics.length > 0 && (
        <Card size="small" title="主要话题" style={{ marginTop: 12 }}>
          <Space wrap>
            {s.topics.map((t, i) => (
              <Tag key={i} color="blue">
                {t}
              </Tag>
            ))}
          </Space>
        </Card>
      )}
    </div>
  );
}

function QATab({ analysis }) {
  const [search, setSearch] = useState('');
  const qa = analysis?.qa_pairs || [];
  const filtered = search
    ? qa.filter(
        (item) =>
          (item.question || '').includes(search) || (item.answer || '').includes(search)
      )
    : qa;

  const columns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 80,
      render: (v) => (v ? formatDuration(v) : '--')
    },
    { title: '问题', dataIndex: 'question', key: 'question', ellipsis: true },
    { title: '回答', dataIndex: 'answer', key: 'answer', ellipsis: true },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 90,
      render: (v) => (v ? <Tag>{v}</Tag> : '--')
    }
  ];

  return (
    <div>
      <Search
        placeholder="搜索问题或回答"
        onSearch={setSearch}
        onChange={(e) => setSearch(e.target.value)}
        style={{ marginBottom: 12, width: 300 }}
      />
      <Table
        dataSource={filtered}
        columns={columns}
        rowKey={(r, i) => i}
        size="small"
        pagination={{ pageSize: 20 }}
        locale={{ emptyText: '暂无问答数据' }}
      />
    </div>
  );
}

function TranscriptTab({ analysis }) {
  const transcript = analysis?.transcript || [];
  return (
    <div style={{ maxHeight: 400, overflowY: 'auto' }}>
      {transcript.length === 0 && <Empty description="暂无文字记录" />}
      <List
        dataSource={transcript}
        renderItem={(item, i) => (
          <List.Item key={i} style={{ padding: '4px 0', alignItems: 'flex-start' }}>
            <Space align="start">
              <Tag color="blue" style={{ minWidth: 50, textAlign: 'center' }}>
                {item.timestamp ? formatDuration(item.timestamp) : '--'}
              </Tag>
              {item.speaker && <Tag color="purple">{item.speaker}</Tag>}
              <Text>{item.text}</Text>
            </Space>
          </List.Item>
        )}
        locale={{ emptyText: '' }}
      />
    </div>
  );
}

function DanmakuTab({ analysis }) {
  const danmaku = analysis?.danmaku || [];
  return (
    <div style={{ maxHeight: 400, overflowY: 'auto' }}>
      {danmaku.length === 0 && <Empty description="暂无弹幕数据" />}
      <List
        dataSource={danmaku}
        renderItem={(item, i) => (
          <List.Item key={i} style={{ padding: '4px 0' }}>
            <Space>
              <Tag color="geekblue">
                {item.timestamp ? formatDuration(item.timestamp) : '--'}
              </Tag>
              {item.user && <Text type="secondary">{item.user}:</Text>}
              <Text>{item.content || item.text}</Text>
            </Space>
          </List.Item>
        )}
        locale={{ emptyText: '' }}
      />
    </div>
  );
}

function StyleTab({ analysis }) {
  const styleAnalysis = analysis?.style_analysis || {};
  if (!styleAnalysis.text && !styleAnalysis.traits) {
    return <Empty description="暂无风格分析" />;
  }
  return (
    <div>
      {styleAnalysis.traits && (
        <Row gutter={[8, 8]} style={{ marginBottom: 12 }}>
          {styleAnalysis.traits.map((t, i) => (
            <Col key={i}>
              <Card size="small" style={{ width: 160 }}>
                <div style={{ textAlign: 'center' }}>
                  <Text strong>{t.name}</Text>
                  <Progress
                    type="circle"
                    percent={Math.round((t.score || 0) * 100)}
                    width={60}
                    style={{ display: 'block', margin: '8px auto 0' }}
                  />
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}
      {styleAnalysis.text && <Paragraph>{styleAnalysis.text}</Paragraph>}
    </div>
  );
}

function AnalysisViewer({ analysis, recordingId }) {
  const tabItems = [
    { key: 'overview', label: '概览', children: <OverviewTab analysis={analysis} /> },
    { key: 'qa', label: '问答对', children: <QATab analysis={analysis} /> },
    { key: 'transcript', label: '文字记录', children: <TranscriptTab analysis={analysis} /> },
    { key: 'danmaku', label: '弹幕', children: <DanmakuTab analysis={analysis} /> },
    { key: 'style', label: '风格分析', children: <StyleTab analysis={analysis} /> }
  ];

  const handleExport = (type) => {
    if (!recordingId) return;
    const url = `${downloadReport(recordingId)}?format=${type}`;
    window.open(url, '_blank');
  };

  return (
    <div>
      {recordingId && (
        <div style={{ marginBottom: 12, textAlign: 'right' }}>
          <Space>
            <Button
              icon={<FileTextOutlined />}
              onClick={() => handleExport('markdown')}
            >
              导出 Markdown
            </Button>
            <Button
              icon={<FileExcelOutlined />}
              onClick={() => handleExport('excel')}
            >
              导出 Excel
            </Button>
          </Space>
        </div>
      )}
      <Tabs items={tabItems} />
    </div>
  );
}

export default AnalysisViewer;
