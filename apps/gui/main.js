const { app, BrowserWindow, ipcMain } = require('electron/main')
const path = require('node:path')

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  win.loadFile('index.html')
}

app.whenReady().then(() => {
ipcMain.handle('pyPefSend', (_, sistema) => {
  return new Promise((resolve, reject) => {
    const spawn = require('child_process').spawn;
    const pythonProcess = spawn('python3', [path.join(__dirname, "../../src/electron.py")]);
    pythonProcess.stdin.write(sistema + '\n');
    pythonProcess.stdin.end();

    let output = '';
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stdout.on('end', () => {
      resolve(output);
      console.log(output);
    });

    let error = '';
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.stderr.on('end', () => {
      if (error) {
        reject(error);
      }
    });

    pythonProcess.on('error', (err) => {
      reject(err);
    });
  });
}); 
  createWindow()
})

/*
Meu JSON vai ser
{
  "barras": [{
    "p0": {
      "inicio": [0, 0, 0]
      "fim": [0, 0, 0]
      "vinculo": [0, 0, 0, 0, 0, 0]
    }
  }],

  "cargas": [
    {
      "pos": [0, 0, 0]
      "f": [0, 1, 0]
    }
  ],

  "momentos": [
    {
      "pos": [0, 0, 0]
      "m": [0, 0, 0]
    }
  ]
}

*/