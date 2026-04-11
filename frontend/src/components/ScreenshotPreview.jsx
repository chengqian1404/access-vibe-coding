import React, { useState, useEffect, useContext } from 'react';
import { Card, Button, Typography, Space, Image, Spin } from 'antd';
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons';
import { takeScreenshot } from '../utils/api';
import { API_BASE_URL } from '../config';
import { AppContext } from '../App';
import { formatDateTime } from '../utils/helpers';

const { Text } = Typography;

function ScreenshotPreview() {
  const { lastWsMessage } = useContext(AppContext);
  const [screenshotUrl, setScreenshotUrl] = useState(null);
  const [timestamp, setTimestamp] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (lastWsMessage?.type === 'screenshot') {
      const url = lastWsMessage.url
        ? lastWsMessage.url.startsWith('http')
          ? lastWsMessage.url
          : `${API_BASE_URL}${lastWsMessage.url}`
        : null;
      setScreenshotUrl(url);
      setTimestamp(lastWsMessage.timestamp || new Date().toISOString());
    }
  }, [lastWsMessage]);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      const data = await takeScreenshot();
      if (data?.url) {
        const url = data.url.startsWith('http') ? data.url : `${API_BASE_URL}${data.url}`;
        setScreenshotUrl(url);
        setTimestamp(data.timestamp || new Date().toISOString());
      }
    } catch (e) {
      // error handled in api.js
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!screenshotUrl) return;
    const a = document.createElement('a');
    a.href = screenshotUrl;
    a.download = `screenshot_${Date.now()}.png`;
    a.click();
  };

  return (
    <Card
      title="截图预览"
      size="small"
      extra={
        <Space>
          <Button size="small" icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>
            刷新截图
          </Button>
          {screenshotUrl && (
            <Button size="small" icon={<DownloadOutlined />} onClick={handleDownload}>
              下载
            </Button>
          )}
        </Space>
      }
    >
      <div
        style={{
          minHeight: 160,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#f5f5f5',
          borderRadius: 4
        }}
      >
        {loading && <Spin />}
        {!loading && screenshotUrl && (
          <Image
            src={screenshotUrl}
            alt="截图"
            style={{ maxWidth: '100%', maxHeight: 320 }}
            preview={{ mask: '查看大图' }}
          />
        )}
        {!loading && !screenshotUrl && (
          <Text type="secondary">暂无截图，点击刷新获取</Text>
        )}
      </div>
      {timestamp && (
        <Text
          type="secondary"
          style={{ fontSize: 11, marginTop: 4, display: 'block' }}
        >
          截图时间: {formatDateTime(timestamp)}
        </Text>
      )}
    </Card>
  );
}

export default ScreenshotPreview;
