import React, { useState, useEffect, useRef, useCallback, createContext } from 'react';
import { ConfigProvider, Layout, notification } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import Sidebar from './components/Sidebar';
import { AccountSetup, Monitor, Recording, Analysis, History, Settings } from './pages';
import { WS_URL } from './config';
import storage, { KEYS } from './utils/storage';
import './styles/index.css';

dayjs.locale('zh-cn');

export const AppContext = createContext({});

const { Content } = Layout;

export const PAGES = {
  ACCOUNT_SETUP: 'account_setup',
  MONITOR: 'monitor',
  RECORDING: 'recording',
  ANALYSIS: 'analysis',
  HISTORY: 'history',
  SETTINGS: 'settings'
};

function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.MONITOR);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsMessages, setWsMessages] = useState([]);
  const [lastWsMessage, setLastWsMessage] = useState(null);
  const [logs, setLogs] = useState([]);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  useEffect(() => {
    const weixinId = storage.get(KEYS.WEIXIN_ID);
    if (!weixinId) {
      setCurrentPage(PAGES.ACCOUNT_SETUP);
    } else {
      const savedPage = storage.get(KEYS.CURRENT_PAGE);
      if (savedPage && Object.values(PAGES).includes(savedPage)) {
        setCurrentPage(savedPage);
      } else {
        setCurrentPage(PAGES.MONITOR);
      }
    }
  }, []);

  const addLog = useCallback((level, message) => {
    setLogs((prev) => {
      const newLog = {
        id: Date.now() + Math.random(),
        level,
        message,
        time: new Date().toISOString()
      };
      const updated = [...prev, newLog];
      return updated.length > 500 ? updated.slice(-500) : updated;
    });
  }, []);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        addLog('info', 'WebSocket 已连接到后端');
        if (reconnectTimer.current) {
          clearTimeout(reconnectTimer.current);
          reconnectTimer.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastWsMessage(data);
          setWsMessages((prev) => {
            const updated = [...prev, data];
            return updated.length > 100 ? updated.slice(-100) : updated;
          });
          if (data.type === 'log_message') {
            addLog(data.level || 'info', data.message || '');
          }
        } catch (e) {
          // ignore parse errors
        }
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      ws.onclose = () => {
        setWsConnected(false);
        wsRef.current = null;
        reconnectTimer.current = setTimeout(connectWebSocket, 3000);
      };
    } catch (e) {
      setWsConnected(false);
      reconnectTimer.current = setTimeout(connectWebSocket, 3000);
    }
  }, [addLog]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, [connectWebSocket]);

  useEffect(() => {
    if (window.electron?.onBackendLog) {
      window.electron.onBackendLog((data) => {
        addLog(data.level || 'info', data.message || '');
      });
    }
  }, [addLog]);

  const navigate = useCallback((page) => {
    setCurrentPage(page);
    storage.set(KEYS.CURRENT_PAGE, page);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case PAGES.ACCOUNT_SETUP:
        return <AccountSetup onComplete={() => navigate(PAGES.MONITOR)} />;
      case PAGES.MONITOR:
        return <Monitor />;
      case PAGES.RECORDING:
        return <Recording />;
      case PAGES.ANALYSIS:
        return <Analysis />;
      case PAGES.HISTORY:
        return <History />;
      case PAGES.SETTINGS:
        return <Settings />;
      default:
        return <Monitor />;
    }
  };

  const showSidebar = currentPage !== PAGES.ACCOUNT_SETUP;

  return (
    <ConfigProvider locale={zhCN} theme={{ token: { colorPrimary: '#1890ff' } }}>
      <AppContext.Provider
        value={{
          currentPage,
          navigate,
          wsConnected,
          lastWsMessage,
          wsMessages,
          logs,
          addLog,
          PAGES
        }}
      >
        <Layout style={{ minHeight: '100vh' }}>
          {showSidebar && (
            <Sidebar
              currentPage={currentPage}
              onNavigate={navigate}
              wsConnected={wsConnected}
            />
          )}
          <Layout>
            <Content
              style={{
                padding: showSidebar ? '16px' : '0',
                background: '#f0f2f5',
                overflow: 'auto'
              }}
            >
              {renderPage()}
            </Content>
          </Layout>
        </Layout>
      </AppContext.Provider>
    </ConfigProvider>
  );
}

export default App;
