const drawCanvas = document.getElementById('drawCanvas');
const drawCtx = drawCanvas.getContext('2d');
const epiCanvas = document.getElementById('epicycleCanvas');
const epiCtx = epiCanvas.getContext('2d');
const clearBtn = document.getElementById('clearBtn');
const epicycleSlider = document.getElementById('epicycleSlider');
const epicycleValue = document.getElementById('epicycleValue');

let drawing = false;
let sampledPoints = [];
let lastPoint = null;
let sampleStep = 0;
let animationId = null;
let fourierSeries = [];
let signalLength = 0;
let time = 0;
let trace = [];
let epicycleLimit = 1;
const maxTraceLength = 1000;
const animationSpeed = 1; // matches discrete sample step

drawCtx.lineWidth = 4;
drawCtx.lineCap = 'round';
drawCtx.strokeStyle = '#222';
drawCtx.fillStyle = '#fff';
drawCtx.fillRect(0, 0, drawCanvas.width, drawCanvas.height);

epiCtx.lineCap = 'round';
epiCtx.lineJoin = 'round';
clearEpicycleCanvas();

function getCanvasPosition(event, canvas) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left) * (canvas.width / rect.width),
    y: (event.clientY - rect.top) * (canvas.height / rect.height)
  };
}

function startDrawing(event) {
  event.preventDefault();
  if (fourierSeries.length) {
    stopAnimation();
    clearEpicycleCanvas();
  }
  drawing = true;
  sampledPoints = [];
  trace = [];
  sampleStep = 0;
  lastPoint = getCanvasPosition(event, drawCanvas);
  sampledPoints.push({ ...lastPoint });
  drawCtx.fillStyle = '#fff';
  drawCtx.fillRect(0, 0, drawCanvas.width, drawCanvas.height);
  drawCtx.beginPath();
  drawCtx.moveTo(lastPoint.x, lastPoint.y);
}

function draw(event) {
  if (!drawing) return;
  const point = getCanvasPosition(event, drawCanvas);
  drawCtx.lineTo(point.x, point.y);
  drawCtx.stroke();
  sampleStep += 1;
  if (sampleStep % 3 === 0) {
    sampledPoints.push({ ...point });
  }
  lastPoint = point;
}

function endDrawing(event) {
  if (!drawing) return;
  drawing = false;
  if (event && event.type === 'pointerup') {
    const point = getCanvasPosition(event, drawCanvas);
    sampledPoints.push({ ...point });
  } else if (lastPoint) {
    sampledPoints.push({ ...lastPoint });
  }
  if (sampledPoints.length < 3) {
    sampledPoints = [];
    return;
  }
  fourierSeries = computeFourier(sampledPoints);
  signalLength = sampledPoints.length * 2;
  time = 0;
  trace = [];
  setupEpicycleSlider();
  startAnimation();
}

function computeFourier(points) {
  const centered = points.map(p => ({
    x: p.x - drawCanvas.width / 2,
    y: p.y - drawCanvas.height / 2
  }));
  const mirrored = centered.concat([...centered].reverse());
  const N = mirrored.length;
  const series = [];
  for (let k = 0; k < N; k += 1) {
    let re = 0;
    let im = 0;
    for (let n = 0; n < N; n += 1) {
      const point = mirrored[n];
      const angle = (-2 * Math.PI * k * n) / N;
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      re += point.x * cos - point.y * sin;
      im += point.x * sin + point.y * cos;
    }
    re /= N;
    im /= N;
    const amplitude = Math.hypot(re, im);
    const phase = Math.atan2(im, re);
    const frequency = k <= N / 2 ? k / N : (k - N) / N;
    series.push({ amplitude, phase, frequency });
  }
  series.sort((a, b) => b.amplitude - a.amplitude);
  return series;
}

function startAnimation() {
  stopAnimation();
  animationId = requestAnimationFrame(stepAnimation);
}

function stopAnimation() {
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
}

function stepAnimation() {
  clearEpicycleCanvas();
  const width = epiCanvas.width;
  const height = epiCanvas.height;
  const offsetX = width / 2;
  const offsetY = height / 2;

  let x = 0;
  let y = 0;

  epiCtx.save();
  epiCtx.translate(offsetX, offsetY);

  epiCtx.lineWidth = 1.5;
  epiCtx.strokeStyle = 'rgba(0, 0, 0, 0.2)';

  const activeEpicycles = Math.min(epicycleLimit, fourierSeries.length);
  for (let i = 0; i < activeEpicycles; i += 1) {
    const coeff = fourierSeries[i];
    const prevX = x;
    const prevY = y;
    const angle = 2 * Math.PI * coeff.frequency * time + coeff.phase;
    x += coeff.amplitude * Math.cos(angle);
    y += coeff.amplitude * Math.sin(angle);

    if (coeff.amplitude < 0.5) {
      continue;
    }

    epiCtx.beginPath();
    epiCtx.arc(prevX, prevY, coeff.amplitude, 0, Math.PI * 2);
    epiCtx.stroke();

    epiCtx.beginPath();
    epiCtx.moveTo(prevX, prevY);
    epiCtx.lineTo(x, y);
    epiCtx.strokeStyle = '#0f7b0f';
    epiCtx.stroke();
    epiCtx.strokeStyle = 'rgba(0, 0, 0, 0.2)';

    epiCtx.fillStyle = '#005fb8';
    epiCtx.beginPath();
    epiCtx.arc(prevX, prevY, 3, 0, Math.PI * 2);
    epiCtx.fill();
  }

  epiCtx.restore();

  trace.push({ x: x + offsetX, y: y + offsetY });
  if (trace.length > maxTraceLength) {
    trace.shift();
  }

  epiCtx.lineWidth = 3;
  epiCtx.strokeStyle = '#111';
  epiCtx.beginPath();
  for (let i = 0; i < trace.length; i += 1) {
    const point = trace[i];
    if (i === 0) {
      epiCtx.moveTo(point.x, point.y);
    } else {
      epiCtx.lineTo(point.x, point.y);
    }
  }
  epiCtx.stroke();

  if (trace.length) {
    const tip = trace[trace.length - 1];
    epiCtx.fillStyle = '#d13438';
    epiCtx.beginPath();
    epiCtx.arc(tip.x, tip.y, 4, 0, Math.PI * 2);
    epiCtx.fill();
  }

  time += animationSpeed;
  if (time >= signalLength) {
    time = 0;
    trace = [];
  }

  animationId = requestAnimationFrame(stepAnimation);
}

function clearEpicycleCanvas() {
  epiCtx.fillStyle = '#fff';
  epiCtx.fillRect(0, 0, epiCanvas.width, epiCanvas.height);
}

function resetAll() {
  stopAnimation();
  sampledPoints = [];
  fourierSeries = [];
  trace = [];
  time = 0;
  lastPoint = null;
  epicycleLimit = 1;
  epicycleSlider.value = '1';
  epicycleSlider.max = '1';
  epicycleSlider.disabled = true;
  epicycleValue.textContent = '1';
  drawCtx.fillStyle = '#fff';
  drawCtx.fillRect(0, 0, drawCanvas.width, drawCanvas.height);
  drawCtx.beginPath();
  clearEpicycleCanvas();
}

drawCanvas.addEventListener('pointerdown', startDrawing);
drawCanvas.addEventListener('pointermove', draw);
drawCanvas.addEventListener('pointerup', endDrawing);
drawCanvas.addEventListener('pointerleave', endDrawing);
drawCanvas.addEventListener('pointercancel', endDrawing);
clearBtn.addEventListener('click', resetAll);

document.addEventListener('touchmove', event => {
  if (event.target === drawCanvas && drawing) {
    event.preventDefault();
  }
}, { passive: false });

epicycleSlider.addEventListener('input', event => {
  const value = Number.parseInt(event.target.value, 10);
  epicycleLimit = Number.isNaN(value) ? epicycleLimit : Math.max(1, value);
  epicycleValue.textContent = epicycleLimit;
  time = 0;
  trace = [];
});

function setupEpicycleSlider() {
  const maxEpicycles = Math.max(1, fourierSeries.length);
  epicycleSlider.max = String(maxEpicycles);
  epicycleLimit = maxEpicycles;
  epicycleSlider.value = String(epicycleLimit);
  epicycleSlider.disabled = false;
  epicycleValue.textContent = epicycleLimit;
}
