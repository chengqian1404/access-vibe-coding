const { app, BrowserWindow, ipcMain, shell, dialog, Tray, Menu, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

app.setName('直播学习分析工具');

let mainWindow = null;
let tray = null;
let backendProcess = null;
const isDev = process.env.NODE_ENV === 'development';

function startBackend() {
  let backendCmd, backendArgs, backendCwd;

  if (isDev) {
    const backendPath = path.join(__dirname, '..', 'backend', 'app', 'main.py');
    if (fs.existsSync(backendPath)) {
      backendCmd = 'python';
      backendArgs = [backendPath];
      backendCwd = path.join(__dirname, '..', 'backend');
    } else {
      console.log('Backend not found at:', backendPath);
      return;
    }
  } else {
    const isWin = process.platform === 'win32';
    const exeName = isWin ? 'main.exe' : 'main';
    const exePath = path.join(process.resourcesPath, 'backend', exeName);
    if (fs.existsSync(exePath)) {
      backendCmd = exePath;
      backendArgs = [];
      backendCwd = path.join(process.resourcesPath, 'backend');
    } else {
      console.log('Packaged backend not found at:', exePath);
      return;
    }
  }

  try {
    backendProcess = spawn(backendCmd, backendArgs, {
      cwd: backendCwd,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env }
    });

    backendProcess.stdout.on('data', (data) => {
      const msg = data.toString();
      console.log('[Backend]', msg);
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('backend-log', { level: 'info', message: msg.trim() });
      }
    });

    backendProcess.stderr.on('data', (data) => {
      const msg = data.toString();
      console.error('[Backend Error]', msg);
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('backend-log', { level: 'error', message: msg.trim() });
      }
    });

    backendProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
      backendProcess = null;
    });

    backendProcess.on('error', (err) => {
      console.error('Failed to start backend:', err);
      backendProcess = null;
    });
  } catch (err) {
    console.error('Error spawning backend:', err);
  }
}

function stopBackend() {
  if (backendProcess) {
    try {
      backendProcess.kill('SIGTERM');
    } catch (e) {
      console.error('Error killing backend:', e);
    }
    backendProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 600,
    frame: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false
    },
    title: '直播学习分析工具',
    show: false
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTray() {
  try {
    const icon = nativeImage.createEmpty();
    tray = new Tray(icon);
    const contextMenu = Menu.buildFromTemplate([
      {
        label: '显示主窗口',
        click: () => {
          if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
          } else {
            createWindow();
          }
        }
      },
      { type: 'separator' },
      {
        label: '退出',
        click: () => {
          app.quit();
        }
      }
    ]);
    tray.setToolTip('直播学习分析工具');
    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => {
      if (mainWindow) {
        mainWindow.show();
        mainWindow.focus();
      }
    });
  } catch (e) {
    console.error('Tray creation error:', e);
  }
}

function setupIPC() {
  ipcMain.handle('open-external-url', async (event, url) => {
    try {
      await shell.openExternal(url);
      return { success: true };
    } catch (e) {
      return { success: false, error: e.message };
    }
  });

  ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
  });

  ipcMain.handle('show-message-box', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
  });
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
  createTray();
  setupIPC();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopBackend();
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

app.on('will-quit', () => {
  stopBackend();
});
