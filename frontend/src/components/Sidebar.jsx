import React, { useState } from 'react';
import { Layout, Menu, Badge, Typography, Button, Tooltip } from 'antd';
import {
  UserOutlined,
  VideoCameraOutlined,
  ReconciliationOutlined,
  BarChartOutlined,
  HistoryOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons';
import { PAGES } from '../App';

const { Sider } = Layout;
const { Text } = Typography;

const menuItems = [
  { key: PAGES.ACCOUNT_SETUP, icon: <UserOutlined />, label: '账号设置' },
  { key: PAGES.MONITOR, icon: <VideoCameraOutlined />, label: '直播监控' },
  { key: PAGES.RECORDING, icon: <ReconciliationOutlined />, label: '录制控制' },
  { key: PAGES.ANALYSIS, icon: <BarChartOutlined />, label: '分析查看' },
  { key: PAGES.HISTORY, icon: <HistoryOutlined />, label: '历史记录' },
  { key: PAGES.SETTINGS, icon: <SettingOutlined />, label: '系统设置' }
];

function Sidebar({ currentPage, onNavigate, wsConnected }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={setCollapsed}
      trigger={null}
      style={{ background: '#001529', minHeight: '100vh' }}
      width={200}
    >
      <div
        style={{
          padding: collapsed ? '16px 8px' : '16px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between'
        }}
      >
        {!collapsed && (
          <Text
            strong
            style={{
              color: '#fff',
              fontSize: 13,
              flex: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            直播学习分析
          </Text>
        )}
        <Tooltip title={wsConnected ? '已连接后端' : '未连接后端'}>
          <Badge
            status={wsConnected ? 'success' : 'error'}
            style={{ cursor: 'default' }}
          />
        </Tooltip>
      </div>

      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[currentPage]}
        items={menuItems}
        onClick={({ key }) => onNavigate(key)}
        style={{ borderRight: 0, marginTop: 8 }}
      />

      <div style={{ position: 'absolute', bottom: 16, width: '100%', textAlign: 'center' }}>
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={() => setCollapsed(!collapsed)}
          style={{ color: 'rgba(255,255,255,0.65)' }}
        />
      </div>
    </Sider>
  );
}

export default Sidebar;
