import React from 'react';
import { Layout, Menu, Typography, Tooltip, Button } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  SettingOutlined,
  HistoryOutlined,
  AppstoreOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BulbOutlined,
  GithubOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;
const { Text } = Typography;

const menuItems = [
  { key: '/', icon: <HomeOutlined />, label: '主页' },
  { key: '/templates', icon: <AppstoreOutlined />, label: '指令模板' },
  { key: '/history', icon: <HistoryOutlined />, label: '历史记录' },
  { key: '/settings', icon: <SettingOutlined />, label: '设置' },
];

function Sidebar({ collapsed, onCollapse, darkMode, onToggleTheme }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={onCollapse}
      trigger={null}
      width={200}
      collapsedWidth={60}
      style={{
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 100,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div className="sidebar-header" style={{ padding: collapsed ? '16px 0' : '16px', textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        {!collapsed ? (
          <div>
            <Text strong style={{ color: '#fff', fontSize: 15, display: 'block' }}>
              Access Vibe
            </Text>
            <Text style={{ color: 'rgba(255,255,255,0.65)', fontSize: 11 }}>
              Coding
            </Text>
          </div>
        ) : (
          <Text strong style={{ color: '#fff', fontSize: 16 }}>AV</Text>
        )}
      </div>

      {/* Navigation Menu */}
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        style={{ flex: 1, borderRight: 0, paddingTop: 8 }}
      />

      {/* Footer actions */}
      <div style={{ padding: collapsed ? '8px 0' : '8px 12px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Tooltip title={collapsed ? (darkMode ? '浅色模式' : '深色模式') : ''} placement="right">
          <Button
            type="text"
            icon={<BulbOutlined />}
            onClick={onToggleTheme}
            style={{ color: 'rgba(255,255,255,0.65)', width: '100%', textAlign: collapsed ? 'center' : 'left' }}
          >
            {!collapsed && (darkMode ? '浅色模式' : '深色模式')}
          </Button>
        </Tooltip>

        <Tooltip title={collapsed ? '折叠/展开' : ''} placement="right">
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => onCollapse(!collapsed)}
            style={{ color: 'rgba(255,255,255,0.65)', width: '100%', textAlign: collapsed ? 'center' : 'left' }}
          >
            {!collapsed && '收起侧栏'}
          </Button>
        </Tooltip>
      </div>
    </Sider>
  );
}

export default Sidebar;
