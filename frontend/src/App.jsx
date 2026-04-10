import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Settings from './pages/Settings';
import History from './pages/History';
import Templates from './pages/Templates';
import './styles/App.css';

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') setDarkMode(true);
  }, []);

  const toggleTheme = () => {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  };

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 8,
        },
      }}
    >
      <AntApp>
        <Router>
          <div className={`app-layout ${darkMode ? 'dark' : 'light'}`}>
            <Sidebar
              collapsed={collapsed}
              onCollapse={setCollapsed}
              darkMode={darkMode}
              onToggleTheme={toggleTheme}
            />
            <main className={`app-content ${collapsed ? 'collapsed' : ''}`}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/history" element={<History />} />
                <Route path="/templates" element={<Templates />} />
              </Routes>
            </main>
          </div>
        </Router>
      </AntApp>
    </ConfigProvider>
  );
}

export default App;
