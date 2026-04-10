import React, { useState } from 'react';
import { Card, Image, Empty, Button, Tooltip, Typography, Spin } from 'antd';
import { ReloadOutlined, ZoomInOutlined, DownloadOutlined } from '@ant-design/icons';

const { Text } = Typography;

function ScreenshotPreview({ screenshot = null, loading = false, onRefresh, title = '截图预览' }) {
  const [visible, setVisible] = useState(false);

  const handleDownload = () => {
    if (!screenshot) return;
    const link = document.createElement('a');
    link.href = `data:image/jpeg;base64,${screenshot}`;
    link.download = `screenshot-${Date.now()}.jpg`;
    link.click();
  };

  return (
    <Card
      className="screenshot-preview"
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Text strong>🖼️ {title}</Text>
        </div>
      }
      extra={
        <div style={{ display: 'flex', gap: 8 }}>
          {screenshot && (
            <>
              <Tooltip title="放大查看">
                <Button size="small" icon={<ZoomInOutlined />} onClick={() => setVisible(true)} />
              </Tooltip>
              <Tooltip title="下载截图">
                <Button size="small" icon={<DownloadOutlined />} onClick={handleDownload} />
              </Tooltip>
            </>
          )}
          {onRefresh && (
            <Tooltip title="刷新截图">
              <Button
                size="small"
                icon={<ReloadOutlined spin={loading} />}
                onClick={onRefresh}
                loading={loading}
              />
            </Tooltip>
          )}
        </div>
      }
      bodyStyle={{ padding: 8, minHeight: 150 }}
    >
      <Spin spinning={loading}>
        {screenshot ? (
          <div style={{ textAlign: 'center' }}>
            <Image
              src={`data:image/jpeg;base64,${screenshot}`}
              style={{
                maxWidth: '100%',
                maxHeight: 300,
                objectFit: 'contain',
                borderRadius: 4,
                cursor: 'zoom-in',
              }}
              preview={{
                visible,
                onVisibleChange: setVisible,
                src: `data:image/jpeg;base64,${screenshot}`,
              }}
              onClick={() => setVisible(true)}
              alt="Screen capture"
            />
          </div>
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={<Text type="secondary">暂无截图</Text>}
            style={{ margin: '20px 0' }}
          />
        )}
      </Spin>
    </Card>
  );
}

export default ScreenshotPreview;
