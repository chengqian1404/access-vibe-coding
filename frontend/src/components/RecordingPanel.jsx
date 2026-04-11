import React, { useState, useEffect, useRef, useContext } from 'react';
import {
  Card,
  Button,
  Select,
  Space,
  Typography,
  Badge,
  Row,
  Col,
  Progress
} from 'antd';
import { PlayCircleOutlined, StopOutlined, CameraOutlined } from '@ant-design/icons';
import {
  startRecording,
  stopRecording,
  getRecordingStatus,
  takeScreenshot,
  getAudioDevices
} from '../utils/api';
import { AppContext } from '../App';
import { formatDuration, formatFileSize, getStatusText } from '../utils/helpers';

const { Text } = Typography;
const { Option } = Select;

function RecordingPanel({ onRecordingStarted, onRecordingStopped }) {
  const { lastWsMessage, addLog } = useContext(AppContext);
  const [status, setStatus] = useState('idle');
  const [duration, setDuration] = useState(0);
  const [fileSize, setFileSize] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [fps, setFps] = useState(10);
  const [audioDevice, setAudioDevice] = useState('');
  const [audioDevices, setAudioDevices] = useState([]);
  const [region, setRegion] = useState('fullscreen');
  const [loading, setLoading] = useState(false);
  const [recordingId, setRecordingId] = useState(null);
  const timerRef = useRef(null);
  const startTimeRef = useRef(null);

  useEffect(() => {
    getAudioDevices()
      .then((data) => {
        if (Array.isArray(data)) setAudioDevices(data);
        else if (data?.devices) setAudioDevices(data.devices);
      })
      .catch(() => {});

    getRecordingStatus()
      .then((data) => {
        if (data) {
          setStatus(data.status || 'idle');
          if (data.duration) setDuration(data.duration);
          if (data.file_size) setFileSize(data.file_size);
          if (data.recording_id) setRecordingId(data.recording_id);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!lastWsMessage) return;
    if (lastWsMessage.type === 'recording_status') {
      setStatus(lastWsMessage.status || 'idle');
      if (lastWsMessage.duration !== undefined) setDuration(lastWsMessage.duration);
      if (lastWsMessage.file_size !== undefined) setFileSize(lastWsMessage.file_size);
    }
    if (lastWsMessage.type === 'audio_level') {
      setAudioLevel(Math.min(100, Math.max(0, (lastWsMessage.level || 0) * 100)));
    }
  }, [lastWsMessage]);

  useEffect(() => {
    if (status === 'recording') {
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now() - duration * 1000;
      }
      timerRef.current = setInterval(() => {
        setDuration(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      if (status !== 'recording') startTimeRef.current = null;
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [status]);

  const handleStart = async () => {
    setLoading(true);
    try {
      const data = await startRecording({ fps, audio_device: audioDevice, region });
      setStatus('recording');
      setDuration(0);
      startTimeRef.current = Date.now();
      setRecordingId(data?.recording_id);
      addLog('info', '开始录制');
      if (onRecordingStarted) onRecordingStarted(data);
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      const data = await stopRecording();
      setStatus('idle');
      addLog('info', '停止录制');
      if (onRecordingStopped) onRecordingStopped(data || { recording_id: recordingId });
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  const handleScreenshot = async () => {
    try {
      await takeScreenshot();
      addLog('info', '已截图');
    } catch (e) {
      // error handled in api.js
    }
  };

  const isRecording = status === 'recording';
  const audioLevelColor =
    audioLevel > 80 ? '#ff4d4f' : audioLevel > 50 ? '#faad14' : '#52c41a';

  return (
    <Card title="录制控制" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Space>
            <Badge status={isRecording ? 'processing' : 'default'} text={getStatusText(status)} />
            {isRecording && (
              <Text type="danger" strong style={{ fontFamily: 'monospace', fontSize: 16 }}>
                {formatDuration(duration)}
              </Text>
            )}
            {fileSize > 0 && <Text type="secondary">{formatFileSize(fileSize)}</Text>}
          </Space>
        </Col>

        <Col span={24}>
          <Row gutter={8} align="middle">
            <Col>
              <Text strong>音量:</Text>
            </Col>
            <Col flex="auto">
              <Progress
                percent={Math.round(audioLevel)}
                strokeColor={audioLevelColor}
                showInfo={false}
                size="small"
                className="audio-level-bar"
              />
            </Col>
            <Col>
              <Text style={{ width: 40 }}>{Math.round(audioLevel)}%</Text>
            </Col>
          </Row>
        </Col>

        <Col span={24}>
          <Space wrap>
            <Select
              value={fps}
              onChange={setFps}
              style={{ width: 110 }}
              disabled={isRecording}
            >
              <Option value={5}>5 FPS</Option>
              <Option value={10}>10 FPS</Option>
              <Option value={15}>15 FPS</Option>
              <Option value={24}>24 FPS</Option>
              <Option value={30}>30 FPS</Option>
            </Select>
            <Select
              value={region}
              onChange={setRegion}
              style={{ width: 130 }}
              disabled={isRecording}
            >
              <Option value="fullscreen">全屏录制</Option>
              <Option value="custom">自定义区域</Option>
            </Select>
            <Select
              value={audioDevice}
              onChange={setAudioDevice}
              style={{ width: 200 }}
              disabled={isRecording}
              placeholder="选择音频设备"
              allowClear
            >
              {audioDevices.map((d, i) => (
                <Option key={d.id || i} value={d.id || d.name}>
                  {d.name}
                </Option>
              ))}
            </Select>
          </Space>
        </Col>

        <Col span={24}>
          <Space>
            {!isRecording ? (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleStart}
                loading={loading}
              >
                开始录制
              </Button>
            ) : (
              <Button
                danger
                icon={<StopOutlined />}
                onClick={handleStop}
                loading={loading}
              >
                停止录制
              </Button>
            )}
            <Button
              icon={<CameraOutlined />}
              onClick={handleScreenshot}
              disabled={!isRecording}
            >
              截图
            </Button>
          </Space>
        </Col>
      </Row>
    </Card>
  );
}

export default RecordingPanel;
