const { app, BrowserWindow, shell } = require('electron');

const SITE_URL = 'https://marca-dagua-site.onrender.com/';

function createWindow() {
  const window = new BrowserWindow({
    title: 'MarcaFlow',
    width: 1180,
    height: 820,
    minWidth: 390,
    minHeight: 640,
    backgroundColor: '#080706',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  window.loadURL(SITE_URL);
  window.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
  window.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith(SITE_URL)) {
      event.preventDefault();
      shell.openExternal(url);
    }
  });
}

app.setAppUserModelId('com.enzocgoncalves.marcaflow');
app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
