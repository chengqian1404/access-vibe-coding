/**
 * Electron Preload Script
 * Exposes safe IPC API to renderer process via contextBridge
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Backend URL
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),

  // Platform
  getPlatform: () => ipcRenderer.invoke('get-platform'),

  // Shell
  openExternal: (url) => ipcRenderer.invoke('open-external', url),

  // Dialogs
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
});
