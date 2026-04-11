import axios from 'axios';
import { notification } from 'antd';
import { API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '请求失败';
    notification.error({ message: '请求错误', description: message, duration: 4 });
    return Promise.reject(error);
  }
);

export const getConfig = () => api.get('/config');
export const updateConfig = (data) => api.post('/config', data);

export const startRecording = (options) => api.post('/recording/start', options || {});
export const stopRecording = () => api.post('/recording/stop');
export const getRecordingStatus = () => api.get('/recording/status');
export const takeScreenshot = () => api.post('/recording/screenshot');

export const startMonitor = (weixinId) => api.post('/monitor/start', { weixin_id: weixinId });
export const stopMonitor = () => api.post('/monitor/stop');
export const getMonitorStatus = () => api.get('/monitor/status');

export const getRecordings = () => api.get('/recordings');
export const getRecording = (id) => api.get(`/recordings/${id}`);
export const deleteRecording = (id) => api.delete(`/recordings/${id}`);

export const startAnalysis = (recordingId) => api.post('/analysis/start', { recording_id: recordingId });
export const getAnalysis = (recordingId) => api.get(`/analysis/${recordingId}`);
export const downloadReport = (recordingId) => `${API_BASE_URL}/api/analysis/${recordingId}/report`;

export const getAudioDevices = () => api.get('/devices/audio');
export const openWeixin = () => api.post('/weixin/open');

export default api;
