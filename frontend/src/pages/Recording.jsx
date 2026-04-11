import React, { useState, useContext, useEffect } from 'react';
import { Row, Col, Steps, Button, Typography, Card, Alert } from 'antd';
import { LoadingOutlined, BarChartOutlined } from '@ant-design/icons';
import RecordingPanel from '../components/RecordingPanel';
import ScreenshotPreview from '../components/ScreenshotPreview';
import LogViewer from '../components/LogViewer';
import { AppContext, PAGES } from '../App';
import { startAnalysis } from '../utils/api';

const { Title, Text } = Typography;

const STEP_LABELS = ['准备', '录制中', '处理中', '完成'];

function Recording() {
  const { navigate, lastWsMessage } = useContext(AppContext);
  const [step, setStep] = useState(0);
  const [recordingId, setRecordingId] = useState(null);
  const [analysisStarted, setAnalysisStarted] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [transcript, setTranscript] = useState([]);

  useEffect(() => {
    if (!lastWsMessage) return;
    if (lastWsMessage.type === 'transcription') {
      setTranscript((prev) => [...prev, lastWsMessage]);
    }
    if (lastWsMessage.type === 'recording_status') {
      if (lastWsMessage.status === 'recording') setStep(1);
      else if (lastWsMessage.status === 'processing') setStep(2);
      else if (lastWsMessage.status === 'completed') setStep(3);
      else if (lastWsMessage.status === 'idle') setStep(0);
    }
  }, [lastWsMessage]);

  const handleRecordingStarted = (data) => {
    setStep(1);
    setRecordingId(data?.recording_id);
    setTranscript([]);
  };

  const handleRecordingStopped = (data) => {
    setStep(2);
    if (data?.recording_id) setRecordingId(data.recording_id);
    setTimeout(() => setStep(3), 2000);
  };

  const handleStartAnalysis = async () => {
    if (!recordingId) return;
    setAnalysisLoading(true);
    try {
      await startAnalysis(recordingId);
      setAnalysisStarted(true);
      navigate(PAGES.ANALYSIS);
    } catch (e) {
      // error handled in api.js
    } finally {
      setAnalysisLoading(false);
    }
  };

  const stepItems = STEP_LABELS.map((title, i) => ({
    title,
    status:
      i < step
        ? 'finish'
        : i === step
        ? step === 1
          ? 'process'
          : 'wait'
        : 'wait',
    icon: i === 1 && step === 1 ? <LoadingOutlined /> : undefined
  }));

  return (
    <div className="recording-page">
      <Title level={4} style={{ marginBottom: 16 }}>
        录制控制
      </Title>

      <Steps items={stepItems} style={{ marginBottom: 24 }} current={step} />

      <Row gutter={[16, 16]}>
        <Col span={14}>
          <RecordingPanel
            onRecordingStarted={handleRecordingStarted}
            onRecordingStopped={handleRecordingStopped}
          />
          <LogViewer />
        </Col>
        <Col span={10}>
          <ScreenshotPreview />

          {transcript.length > 0 && (
            <Card title="实时转录" size="small" style={{ marginTop: 16 }}>
              <div style={{ maxHeight: 150, overflowY: 'auto', fontSize: 13 }}>
                {transcript.slice(-20).map((t, i) => (
                  <div key={i} style={{ padding: '2px 0' }}>
                    {t.text}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {step >= 3 && !analysisStarted && (
            <Card style={{ marginTop: 16 }}>
              <Alert
                message="录制完成"
                description="录制已停止，可以开始 AI 分析了。"
                type="success"
                showIcon
                style={{ marginBottom: 12 }}
              />
              <Button
                type="primary"
                icon={<BarChartOutlined />}
                block
                onClick={handleStartAnalysis}
                loading={analysisLoading}
              >
                开始 AI 分析
              </Button>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
}

export default Recording;
