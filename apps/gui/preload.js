const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('bridge', {
  pyPefSend: (sistema) => ipcRenderer.invoke('pyPefSend', sistema)
  // we can also expose variables, not just functions
})

