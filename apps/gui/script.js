

class Ponto {
  constructor(x, y, fx, fy, mz, resolvido) {
    this.x = x;
    this.y = y;
    this.f = new Vector3(fx, fy, 0)
    this.m = new Vector3(0, 0, mz)
    this.resolvido = resolvido;
    this.Vinculo = {
      f: new Vector3(false, false, false),
      m: new Vector3(false, false, false)
    };
  }
}

class Vector3 {
  constructor(x, y, z) {
    this.x = x;
    this.y = y;
    this.z = z;
  }
}


class CargaConcentrada {
  constructor(f, pos) {
    this.f = f; // Vector3
    this.pos = pos; // Vector3
  }
}

let cargas = [];

const scaleFactor = 10; // adjust this value to change the size of the arrows

function drawArrow(ctx, x, y, dx, dy) {
  const headLength = 10;
  const headAngle = Math.PI / 6;

  // Draw the line
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + dx, y + dy);
  ctx.strokeStyle = 'black';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Draw the arrow head
  ctx.beginPath();
  ctx.moveTo(x + dx, y + dy);
  ctx.lineTo(x + dx - headLength * Math.cos(Math.atan2(dy, dx) - headAngle), y + dy - headLength * Math.sin(Math.atan2(dy, dx) - headAngle));
  ctx.lineTo(x + dx - headLength * Math.cos(Math.atan2(dy, dx) + headAngle), y + dy - headLength * Math.sin(Math.atan2(dy, dx) + headAngle));
  ctx.closePath();
  ctx.fillStyle = 'black';
  ctx.fill();
}

function drawCargas() {
  ctx.strokeStyle = 'black';
  ctx.lineWidth = 2;
  ctx.setLineDash([])

  for (const carga of cargas) {
    const f = carga.f;
    const pos = carga.pos;

    const x = pos.x * scaleFactor;
    const y = pos.y * scaleFactor;
    const dx = f.x * scaleFactor;
    const dy = f.y * scaleFactor;

    drawArrow(ctx, x, y, dx, dy);
  }
}


const clearButton = document.getElementById('clear-btn')

clearButton.addEventListener('click', (e) => {
  vertices = []
  cargas = []
  selectedVertex = null
  const popup = document.getElementById('vertex-popup');
  popup.style.display = 'none';
  draw()
  document.getElementById('selected-vertex').innerHTML = '';
})

// Get the canvas element
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Set the canvas dimensions
canvas.width = 600;
canvas.height = 400;


// Initialize variables
let vertices = [];
let isDrawing = false;
let lastVertex = null;
let mode = 'drawing'; // 'drawing' or 'select'
let selectedVertex = null;

// Add event listeners
canvas.addEventListener('mousedown', (e) => {
  if (mode === 'drawing' && !isDrawing) {
    isDrawing = true;
    lastVertex = new Ponto(e.offsetX, e.offsetY, 0, 0, 0, false);
    vertices.push(lastVertex);
  } else if (mode === 'select') {
    for (let i = vertices.length - 1; i >= 0; i--) {
      const vertex = vertices[i];
      if (Math.abs(vertex.x - e.offsetX) < 5 && Math.abs(vertex.y - e.offsetY) < 5) {
        selectedVertex = i;
        forcesHtmlString = vertex.resolvido ? `fx = ${vertex.f.x}, fy = ${vertex.f.y}, fz = ${vertex.f.z}` : "";
        momentsHtmlString = vertex.resolvido ? `mx = ${vertex.m.x} my = ${vertex.m.y}, mz = ${vertex.m.z}` : "";
        document.getElementById('selected-vertex').innerHTML = `Selected vertex: x = ${vertex.x}, y = ${vertex.y} <br> ${forcesHtmlString} <br> ${momentsHtmlString}`;
        
        // Show the popup
        const popup = document.getElementById('vertex-popup');
        popup.style.display = 'block';
        document.getElementById('vertex-x').value = vertex.x;
        document.getElementById('vertex-y').value = vertex.y;
        
        // Set the radio buttons to the current values
        const f = vertex.Vinculo.f;
        const m = vertex.Vinculo.m;
        document.getElementById('f-x-1').checked = f.x;
        document.getElementById('f-x-0').checked = !f.x;
        document.getElementById('f-y-1').checked = f.y;
        document.getElementById('f-y-0').checked = !f.y;
        document.getElementById('f-z-1').checked = f.z;
        document.getElementById('f-z-0').checked = !f.z;
        document.getElementById('m-x-1').checked = m.x;
        document.getElementById('m-x-0').checked = !m.x;
        document.getElementById('m-y-1').checked = m.y;
        document.getElementById('m-y-0').checked = !m.y;
        document.getElementById('m-z-1').checked = m.z;
        document.getElementById('m-z-0').checked = !m.z;
        
        // Add an event listener to the update button
        document.getElementById('update-vertex').addEventListener('click', () => {
          const newX = parseInt(document.getElementById('vertex-x').value);
          const newY = parseInt(document.getElementById('vertex-y').value);
          const newVertex = new Ponto(newX, newY, 0, 0, 0, false);
          newVertex.Vinculo = {
            f: {
              x: document.getElementById('f-x-1').checked,
              y: document.getElementById('f-y-1').checked,
              z: document.getElementById('f-z-1').checked
            },
            m: {
              x: document.getElementById('m-x-1').checked,
              y: document.getElementById('m-y-1').checked,
              z: document.getElementById('m-z-1').checked
            }
          };
          
          vertices = vertices.map((v, i) => i === selectedVertex ? newVertex : v);
          draw(); // Update the canvas
        });
        
        return;
      }
    }

  }
});

canvas.addEventListener('mousemove', (e) => {
  if (isDrawing) {
    // Don't register vertex if the user holds down on the mouse button
    return;
  }
});

canvas.addEventListener('mouseup', () => {
  isDrawing = false;
});


// Draw a line between two vertices
function drawLine(v1, v2) {
  ctx.beginPath();
  ctx.moveTo(v1.x, v1.y);
  ctx.lineTo(v2.x, v2.y);
  ctx.stroke();
}

// Draw a vertex
function drawVertex(vertex, isSelected) {
  ctx.beginPath();
  ctx.arc(vertex.x, vertex.y, 3, 0, 2 * Math.PI);
  ctx.fillStyle = isSelected ? 'blue' : 'red';
  ctx.fill();
}

// Draw all vertices and lines
function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid(); // draw the grid
  drawCargas()
    ctx.setLineDash([])
    ctx.strokeStyle = '#121212'
  for (let i = 1; i < vertices.length; i++) {
    drawLine(vertices[i - 1], vertices[i]);
  }
  for (let i = 0; i < vertices.length; i++) {
    const vertex = vertices[i];
    drawVertex(vertex, i === selectedVertex);
  }
}

function drawGrid() {
  ctx.strokeStyle = '#ccc'; // light gray
  ctx.lineWidth = 0.5;
  ctx.setLineDash([2, 2]); // dashed line

  for (let x = 0; x <= canvas.width; x += 20) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }

  for (let y = 0; y <= canvas.height; y += 20) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
}

// Toggle mode
document.getElementById('mode-toggle').addEventListener('click', () => {
  mode = mode === 'drawing' ? 'select' : 'drawing';
  document.getElementById('mode-toggle').textContent = `Toggle Mode (${mode})`;
});

// Update the canvas
setInterval(draw, 32); // 16ms = 60fps


document.getElementById('vinculo-preset').addEventListener('change', (e) => {
  const preset = e.target.value;
  switch (preset) {
    case 'ApoioSimplesX':
      document.getElementById('f-x-1').checked = true;
      document.getElementById('f-y-0').checked = true;
      document.getElementById('f-z-0').checked = true;
      document.getElementById('m-x-0').checked = true;
      document.getElementById('m-y-0').checked = true;
      document.getElementById('m-z-0').checked = true;
      break;
    case 'ApoioSimplesY':
      document.getElementById('f-x-0').checked = true;
      document.getElementById('f-y-1').checked = true;
      document.getElementById('f-z-0').checked = true;
      document.getElementById('m-x-0').checked = true;
      document.getElementById('m-y-0').checked = true;
      document.getElementById('m-z-0').checked = true;
      break;
    case 'ApoioSimplesZ':
      document.getElementById('f-x-0').checked = true;
      document.getElementById('f-y-0').checked = true;
      document.getElementById('f-z-1').checked = true;
      document.getElementById('m-x-0').checked = true;
      document.getElementById('m-y-0').checked = true;
      document.getElementById('m-z-0').checked = true;
      break;
    case 'Articulacao':
      document.getElementById('f-x-1').checked = true;
      document.getElementById('f-y-1').checked = true;
      document.getElementById('f-z-1').checked = true;
      document.getElementById('m-x-0').checked = true;
      document.getElementById('m-y-0').checked = true;
      document.getElementById('m-z-0').checked = true;
      break;
    case 'Engaste':
      document.getElementById('f-x-1').checked = true;
      document.getElementById('f-y-1').checked = true;
      document.getElementById('f-z-1').checked = true;
      document.getElementById('m-x-1').checked = true;
      document.getElementById('m-y-1').checked = true;
      document.getElementById('m-z-1').checked = true;
      break;
    case 'Nulo':
      document.getElementById('f-x-0').checked = true;
      document.getElementById('f-y-0').checked = true;
      document.getElementById('f-z-0').checked = true;
      document.getElementById('m-x-0').checked = true;
      document.getElementById('m-y-0').checked = true;
      document.getElementById('m-z-0').checked = true;
      break;
  }
});

const addCargaBtn = document.getElementById('add-carga-btn');
  
addCargaBtn.addEventListener('click', () => {
  const fx = parseFloat(document.getElementById('fx').value);
  const fy = parseFloat(document.getElementById('fy').value);
  const fz = parseFloat(document.getElementById('fz').value);
  const px = parseFloat(document.getElementById('px').value);
  const py = parseFloat(document.getElementById('py').value);
  const pz = parseFloat(document.getElementById('pz').value);

  const newCarga = new CargaConcentrada(new Vector3(fx, fy, fz), new Vector3(px, py, pz));
  cargas = [...cargas, newCarga]; // Use the spread operator to add the new carga to the array
  draw(); // Update the canvas
});

document.getElementById('preset').addEventListener('change', (e) => {
  if (e.target.value === '0') {
    vertices = [];
    cargas = [];

    const inicio = new Ponto(0, 0, 0, 0, 0, false);
    inicio.Vinculo = {
      f: new Vector3(true, true, true),
      m: new Vector3(true, true, true) // Engaste
    };

    const fim = new Ponto(100, 0, 0, 0, 0, false);
    fim.Vinculo = {
      f: new Vector3(false, false, false),
      m: new Vector3(false, false, false) // Nulo
    };

    const barra = {
      inicio: inicio,
      fim: fim
    };

    vertices.push(inicio);
    vertices.push(fim);

    draw();
  }
});


function notNulo(v) {
  return !(v.f.x == 0 && v.f.y == 0 && v.f.z == 0 && v.m.x == 0 && v.m.y == 0 && v.m.z == 0)
}

const solve = document.getElementById("solve-btn")
solve.addEventListener('click', async () => {
  const response = await window.bridge.pyPefSend(JSON.stringify({cargas: cargas, vertices: [...vertices]}))
  reactions = JSON.parse(response)
  console.log(reactions)
  let j = 0;
  vertices = vertices.map((v, i) => {
    if (notNulo(v.Vinculo)) {
      console.log("not null!")
      console.log(reactions)
      let p = new Ponto(v.x, v.y, reactions[j].f[0], reactions[j].f[1], reactions[j].m[2], true)
      j++;
      return p;
    }
    return v;
  }
  )
  console.log(vertices)
})

/* Testing */
// const func = async () => {
//   const response = await window.bridge.pyPefSend()
//   console.log(response) // prints out 'pong'
// }

// func()

