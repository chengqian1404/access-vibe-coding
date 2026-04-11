import React, { useState, useEffect, useContext } from 'react';
import {
  Select,
  Button,
  Card,
  Progress,
  Typography,
  Space,
  Alert,
  Spin
} from 'antd';
import { PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import AnalysisViewer from '../components/AnalysisViewer';
import { getRecordings, startAnalysis, getAnalysis } from '../utils/api';
import { AppContext } from '../App';
import { formatDateTime } from '../utils/helpers';

const { Title, Text } = Typography;
const { Option } = Select;

function Analysis() {
  const { lastWsMessage } = useContext(AppContext);
  const [recordings, setRecordings] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [progress, setProgress] = useState(0);
  const [analysisStatus, setAnalysisStatus] = useState('idle');
  const [loading, setLoading] = useState(false);
  const [startLoading, setStartLoading] = useState(false);

  useEffect(() => {
    getRecordings()
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.recordings || [];
        setRecordings(list);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!lastWsMessage) return;
    if (lastWsMessage.type === 'analysis_progress') {
      setProgress(lastWsMessage.progress || 0);
      setAnalysisStatus(lastWsMessage.status || 'analysing');
      if (lastWsMessage.status === 'done' && selectedId) {
        loadAnalysis(selectedId);
      }
    }
  }, [lastWsMessage, selectedId]);

  const loadAnalysis = async (id) => {
    setLoading(true);
    try {
      const data = await getAnalysis(id);
      setAnalysis(data);
      setAnalysisStatus(data?.status || 'done');
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (id) => {
    setSelectedId(id);
    setAnalysis(null);
    setAnalysisStatus('idle');
    setProgress(0);
    loadAnalysis(id);
  };

  const handleStartAnalysis = async () => {
    if (!selectedId) return;
    setStartLoading(true);
    setAnalysisStatus('analysing');
    setProgress(0);
    try {
      await startAnalysis(selectedId);
    } catch (e) {
      // error handled in api.js
    } finally {
      setStartLoading(false);
    }
  };

  return (
    <div className="analysis-page">
      <Title level={4} style={{ marginBottom: 16 }}>
        分析查看
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Text strong>选择录制：</Text>
          <Select
            value={selectedId}
            onChange={handleSelect}
            style={{ width: 320 }}
            placeholder="选择录制文件"
          >
            {recordings.map((r) => (
              <Option key={r.id} value={r.id}>
                {r.title || r.id}{' '}
                {r.created_at ? `(${formatDateTime(r.created_at)})` : ''}
              </Option>
            ))}
          </Select>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleStartAnalysis}
            disabled={!selectedId}
            loading={startLoading}
          >
            开始分析
          </Button>
          {selectedId && (
            <Button
              icon={<ReloadOutlined />}
              onClick={() => loadAnalysis(selectedId)}
              loading={loading}
            >
              刷新
            </Button>
          )}
        </Space>
      </Card>

      {analysisStatus === 'analysing' && (
        <Card style={{ marginBottom: 16 }}>
          <Text>分析进度：</Text>
          <Progress percent={Math.round(progress)} status="active" />
        </Card>
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin size="large" tip="加载中..." />
        </div>
      )}

      {!loading && analysis && (
        <Card>
          <AnalysisViewer analysis={analysis} recordingId={selectedId} />
        </Card>
      )}

      {!loading && !analysis && selectedId && analysisStatus !== 'analysing' && (
        <Alert message="暂无分析数据，请点击开始分析。" type="info" showIcon />
      )}

      {!selectedId && (
        <Alert message="请先选择一个录制文件。" type="info" showIcon />
      )}
    </div>
  );
}

export default Analysis;
