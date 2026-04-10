import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Row, Col, Space, Typography, Alert, Badge } from 'antd';
import axios from 'axios';
import InstructionInput from '../components/InstructionInput';
import ExecutionPanel from '../components/ExecutionPanel';
import LogViewer from '../components/LogViewer';
import ScreenshotPreview from '../components/ScreenshotPreview';
import { getBackendUrl, getWsUrl } from '../config';

const { Title, Text } = Typography;

function Home() {
  const [executionStatus, setExecutionStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [logs, setLogs] = useState([]);
  const [screenshot, setScreenshot] = useState(null);
  const [parsedInstruction, setParsedInstruction] = useState(null);
  const [result, setResult] = useState(null);
  const [backendOnline, setBackendOnline] = useState(null);
  const [lastInstruction, setLastInstruction] = useState('');
  const wsRef = useRef(null);

  const addLog = useCallback((level, msg) => {
    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    setLogs(prev => [...prev.slice(-199), { level, message: msg, time }]);
  }, []);

  // Check backend health
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const baseUrl = await getBackendUrl();
        await axios.get(`${baseUrl}/health`, { timeout: 3000 });
        setBackendOnline(true);
      } catch {
        setBackendOnline(false);
      }
    };
    checkBackend();
    const timer = setInterval(checkBackend, 10000);
    return () => clearInterval(timer);
  }, []);

  // WebSocket connection
  const connectWs = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    try {
      const wsUrl = await getWsUrl();
      const ws = new WebSocket(`${wsUrl}/ws/execution`);

      ws.onopen = () => addLog('info', 'WebSocket 连接成功');
      ws.onclose = () => addLog('debug', 'WebSocket 已断开');
      ws.onerror = () => addLog('error', 'WebSocket 连接错误');

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWsMessage(data);
        } catch (e) {
          console.error('Failed to parse WS message:', e);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      addLog('error', `WebSocket 连接失败: ${err.message}`);
    }
  }, [addLog]);

  const handleWsMessage = useCallback((data) => {
    switch (data.type) {
      case 'connected':
        addLog('success', '已连接到后端服务');
        break;
      case 'progress':
        setExecutionStatus(data.stage || 'executing');
        setProgress(data.progress || 0);
        setMessage(data.message || '');
        if (data.screenshot) setScreenshot(data.screenshot);
        if (data.parsed) setParsedInstruction(data.parsed);
        addLog('info', data.message || '');
        break;
      case 'complete':
        setExecutionStatus(data.success ? 'success' : 'error');
        setProgress(100);
        setResult(data.result);
        if (data.result?.final_screenshot) setScreenshot(data.result.final_screenshot);
        addLog(data.success ? 'success' : 'error', data.message || '执行完成');
        break;
      case 'error':
        setExecutionStatus('error');
        addLog('error', data.message || '执行出错');
        break;
    }
  }, [addLog]);

  const handleSubmit = useCallback(async (instruction) => {
    setLastInstruction(instruction);
    setExecutionStatus('parsing');
    setProgress(5);
    setMessage('正在连接服务...');
    setParsedInstruction(null);
    setResult(null);
    addLog('info', `开始执行: ${instruction}`);

    // Try WebSocket first
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'execute',
        instruction,
      }));
      return;
    }

    // Fall back to HTTP API
    try {
      const baseUrl = await getBackendUrl();

      setExecutionStatus('parsing');
      setProgress(20);
      setMessage('正在解析指令...');
      addLog('info', '调用 LLM 解析指令...');

      const parseRes = await axios.post(`${baseUrl}/api/v1/instruction/run`, {
        instruction,
      });

      const { parsed, result } = parseRes.data;
      setParsedInstruction(parsed);
      setProgress(100);

      if (result?.final_screenshot) setScreenshot(result.final_screenshot);

      if (parseRes.data.success) {
        setExecutionStatus('success');
        setResult(result);
        addLog('success', `执行成功！共 ${result?.total_steps || 0} 步`);
      } else {
        setExecutionStatus('error');
        setResult(result);
        addLog('error', result?.error || '执行失败');
      }
    } catch (err) {
      setExecutionStatus('error');
      const errMsg = err.response?.data?.detail || err.message || '未知错误';
      addLog('error', `执行失败: ${errMsg}`);
      setResult({ error: errMsg });
    }
  }, [addLog]);

  const handleRetry = () => {
    if (lastInstruction) handleSubmit(lastInstruction);
  };

  const handleRefreshScreenshot = async () => {
    try {
      const baseUrl = await getBackendUrl();
      const res = await axios.get(`${baseUrl}/api/v1/screenshot`);
      if (res.data.screenshot) setScreenshot(res.data.screenshot);
    } catch (err) {
      addLog('error', '截图失败');
    }
  };

  const isExecuting = ['parsing', 'parsed', 'executing'].includes(executionStatus);

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>
          🎯 Access Vibe Coding
        </Title>
        <Space>
          <Badge
            status={backendOnline === null ? 'processing' : backendOnline ? 'success' : 'error'}
            text={
              <Text style={{ fontSize: 12 }}>
                {backendOnline === null ? '检测中...' : backendOnline ? '后端在线' : '后端离线'}
              </Text>
            }
          />
        </Space>
      </div>

      {backendOnline === false && (
        <Alert
          message="后端服务未连接"
          description="请确保 Python 后端已启动。运行 python backend/main.py"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={[16, 16]}>
        {/* Left column: input + execution */}
        <Col xs={24} lg={14}>
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            <InstructionInput onSubmit={handleSubmit} loading={isExecuting} />
            <ExecutionPanel
              status={executionStatus}
              progress={progress}
              message={message}
              result={result}
              parsed={parsedInstruction}
              onRetry={handleRetry}
            />
            <LogViewer logs={logs} onClear={() => setLogs([])} />
          </Space>
        </Col>

        {/* Right column: screenshot */}
        <Col xs={24} lg={10}>
          <ScreenshotPreview
            screenshot={screenshot}
            loading={false}
            onRefresh={handleRefreshScreenshot}
            title="Access 截图"
          />
        </Col>
      </Row>
    </div>
  );
}

export default Home;
