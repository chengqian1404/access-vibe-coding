import React, { useState, useContext, useEffect } from 'react';
import { Row, Col, Card, Statistic, Alert, Button, Typography, notification } from 'antd';
import {
  VideoCameraOutlined,
  ThunderboltOutlined,
  PlayCircleOutlined
} from '@ant-design/icons';
import MonitorPanel from '../components/MonitorPanel';
import LogViewer from '../components/LogViewer';
import { AppContext, PAGES } from '../App';

const { Title } = Typography;

function Monitor() {
  const { navigate, lastWsMessage } = useContext(AppContext);
  const [totalSessions, setTotalSessions] = useState(0);
  const [liveEvents, setLiveEvents] = useState(0);
  const [liveAlert, setLiveAlert] = useState(null);

  useEffect(() => {
    if (lastWsMessage?.type === 'live_detected') {
      setLiveEvents((c) => c + 1);
      setLiveAlert(lastWsMessage);
      notification.success({
        message: '检测到直播！',
        description: '视频号开始直播了，点击开始录制。',
        duration: 0,
        key: 'live-detected',
        btn: (
          <Button
            type="primary"
            size="small"
            onClick={() => {
              navigate(PAGES.RECORDING);
              notification.destroy('live-detected');
            }}
          >
            开始录制
          </Button>
        )
      });
    }
  }, [lastWsMessage, navigate]);

  const handleLiveDetected = (data) => {
    setLiveEvents((c) => c + 1);
    setLiveAlert(data);
  };

  return (
    <div className="monitor-page">
      <Title level={4} style={{ marginBottom: 16 }}>
        直播监控
      </Title>

      {liveAlert && (
        <Alert
          message="正在直播！"
          description="已检测到目标视频号正在直播，建议立即开始录制。"
          type="success"
          showIcon
          style={{ marginBottom: 16 }}
          closable
          action={
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={() => navigate(PAGES.RECORDING)}
            >
              开始录制
            </Button>
          }
          onClose={() => setLiveAlert(null)}
        />
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="监控会话"
              value={totalSessions}
              prefix={<VideoCameraOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="检测到直播"
              value={liveEvents}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: liveEvents > 0 ? '#52c41a' : undefined }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="今日录制" value={0} prefix={<PlayCircleOutlined />} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={14}>
          <MonitorPanel onLiveDetected={handleLiveDetected} />
        </Col>
        <Col span={10}>
          <LogViewer />
        </Col>
      </Row>
    </div>
  );
}

export default Monitor;
