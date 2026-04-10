/**
 * Frontend API configuration
 */

// Detect if running in Electron
const isElectron = typeof window !== 'undefined' && window.electronAPI !== undefined;

// Backend API base URL
export const getBackendUrl = async () => {
  if (isElectron) {
    return window.electronAPI.getBackendUrl();
  }
  return import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8765';
};

export const getWsUrl = async () => {
  const httpUrl = await getBackendUrl();
  return httpUrl.replace('http://', 'ws://').replace('https://', 'wss://');
};

// App configuration
export const APP_CONFIG = {
  name: 'Access Vibe Coding',
  version: '1.0.0',
  description: 'AI 驱动的 Microsoft Access 自动化工具',
};
