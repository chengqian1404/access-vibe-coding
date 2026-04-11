import dayjs from 'dayjs';

export function formatDuration(seconds) {
  if (!seconds && seconds !== 0) return '--';
  const s = Math.floor(seconds);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) {
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  }
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
}

export function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return '--';
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

export function formatDateTime(date) {
  if (!date) return '--';
  return dayjs(date).format('YYYY年MM月DD日 HH:mm:ss');
}

export function formatDate(date) {
  if (!date) return '--';
  return dayjs(date).format('YYYY-MM-DD HH:mm');
}

export function getStatusColor(status) {
  const map = {
    idle: 'default',
    recording: 'processing',
    processing: 'warning',
    completed: 'success',
    error: 'error',
    monitoring: 'processing',
    live_detected: 'success',
    stopped: 'default',
    running: 'processing',
    analysing: 'processing',
    done: 'success',
    failed: 'error'
  };
  return map[status] || 'default';
}

export function getStatusText(status) {
  const map = {
    idle: '空闲',
    recording: '录制中',
    processing: '处理中',
    completed: '已完成',
    error: '出错',
    monitoring: '监控中',
    live_detected: '检测到直播',
    stopped: '已停止',
    running: '运行中',
    analysing: '分析中',
    done: '完成',
    failed: '失败',
    pending: '等待中'
  };
  return map[status] || status || '未知';
}
