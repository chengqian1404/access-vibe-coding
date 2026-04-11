import React, { useState, useEffect, useContext } from 'react';
import {
  Card,
  Button,
  Input,
  Switch,
  Select,
  Space,
  Typography,
  Badge,
  Row,
  Col,
  Alert
} from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import { startMonitor, stopMonitor, getMonitorStatus } from '../utils/api';
import storage, { KEYS } from '../utils/storage';
import { AppContext } from '../App';
import { formatDateTime } from '../utils/helpers';

const { Text } = Typography;
const { Option } = Select;

function MonitorPanel({ onLiveDetected }) {
  const { lastWsMessage, addLog } = useContext(AppContext);
  const [weixinId, setWeixinId] = useState(storage.get(KEYS.WEIXIN_ID, ''));
  const [status, setStatus] = useState('idle');
  const [lastChecked, setLastChecked] = useState(null);
  const [autoOpen, setAutoOpen] = useState(false);
  const [checkInterval, setCheckInterval] = useState(30);
  const [loading, setLoading] = useState(false);
  const [liveUrl, setLiveUrl] = useState(null);

  useEffect(() => {
    getMonitorStatus()
      .then((data) => {
        if (data) {
          setStatus(data.status || 'idle');
          setLastChecked(data.last_checked);
          if (data.weixin_id) setWeixinId(data.weixin_id);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!lastWsMessage) return;
    if (lastWsMessage.type === 'monitor_status') {
      setStatus(lastWsMessage.status || 'idle');
      setLastChecked(lastWsMessage.last_checked);
    }
    if (lastWsMessage.type === 'live_detected') {
      setStatus('live_detected');
      setLiveUrl(lastWsMessage.url);
      if (onLiveDetected) onLiveDetected(lastWsMessage);
      addLog('info', `检测到直播: ${lastWsMessage.url || ''}`);
    }
  }, [lastWsMessage, onLiveDetected, addLog]);

  const handleStart = async () => {
    if (!weixinId.trim()) return;
    setLoading(true);
    try {
      await startMonitor(weixinId.trim());
      storage.set(KEYS.WEIXIN_ID, weixinId.trim());
      setStatus('monitoring');
      addLog('info', `开始监控: ${weixinId}`);
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopMonitor();
      setStatus('idle');
      addLog('info', '已停止监控');
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  const isMonitoring = status === 'monitoring' || status === 'live_detected';

  const statusConfig = {
    idle: { badge: 'default', text: '未开始' },
    monitoring: { badge: 'processing', text: '监控中' },
    live_detected: { badge: 'success', text: '检测到直播' },
    error: { badge: 'error', text: '出错' }
  };
  const sc = statusConfig[status] || statusConfig.idle;

  return (
    <Card title="监控控制" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>视频号ID：</Text>
              <Input
                placeholder="输入视频号ID"
                value={weixinId}
                onChange={(e) => setWeixinId(e.target.value)}
                disabled={isMonitoring}
                style={{ width: 240, marginLeft: 8 }}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <Text strong>状态：</Text>
              <Badge status={sc.badge} text={sc.text} />
            </div>
            {lastChecked && (
              <Text type="secondary">最后检测: {formatDateTime(lastChecked)}</Text>
            )}
          </Space>
        </Col>

        <Col span={24}>
          <Space wrap>
            <Select
              value={checkInterval}
              onChange={setCheckInterval}
              style={{ width: 140 }}
              disabled={isMonitoring}
            >
              <Option value={15}>每15秒检测</Option>
              <Option value={30}>每30秒检测</Option>
              <Option value={60}>每60秒检测</Option>
              <Option value={120}>每2分钟检测</Option>
            </Select>
            <Switch
              checked={autoOpen}
              onChange={setAutoOpen}
              checkedChildren="自动打开微信"
              unCheckedChildren="手动打开微信"
            />
          </Space>
        </Col>

        <Col span={24}>
          <Space>
            {!isMonitoring ? (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleStart}
                loading={loading}
                disabled={!weixinId.trim()}
              >
                开始监控
              </Button>
            ) : (
              <Button
                danger
                icon={<PauseCircleOutlined />}
                onClick={handleStop}
                loading={loading}
              >
                停止监控
              </Button>
            )}
          </Space>
        </Col>

        {status === 'live_detected' && liveUrl && (
          <Col span={24}>
            <Alert
              message="检测到直播！"
              description={`直播地址: ${liveUrl}`}
              type="success"
              showIcon
              action={
                <Button
                  size="small"
                  type="primary"
                  onClick={() => {
                    if (window.electron?.openExternal) window.electron.openExternal(liveUrl);
                  }}
                >
                  打开
                </Button>
              }
            />
          </Col>
        )}
      </Row>
    </Card>
  );
}

export default MonitorPanel;
