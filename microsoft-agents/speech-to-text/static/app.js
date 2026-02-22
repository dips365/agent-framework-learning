const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const clearBtn = document.getElementById("clearBtn");
const notes = document.getElementById("notes");
const statusEl = document.getElementById("status");
const meterText = document.getElementById("meterText");
const lastUpdate = document.getElementById("lastUpdate");

const TARGET_SAMPLE_RATE = 16000;
const BUFFER_SIZE = 4096;

let ws = null;
let audioContext = null;
let processor = null;
let source = null;
let mediaStream = null;

function setStatus(label, isLive) {
  statusEl.textContent = label;
  statusEl.classList.toggle("live", isLive);
  statusEl.classList.toggle("idle", !isLive);
}

function updateTimestamp() {
  const now = new Date();
  lastUpdate.textContent = `Last update: ${now.toLocaleTimeString()}`;
}

function appendText(text, isFinal) {
  if (!text) return;
  const current = notes.value.trim();
  const spacer = current ? " " : "";
  notes.value = `${current}${spacer}${text}`.trim();
  if (isFinal) {
    notes.value += " ";
  }
  updateTimestamp();
}

function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {
  if (outputSampleRate >= inputSampleRate) {
    return buffer;
  }
  const ratio = inputSampleRate / outputSampleRate;
  const newLength = Math.round(buffer.length / ratio);
  const result = new Float32Array(newLength);
  let offsetResult = 0;
  let offsetBuffer = 0;

  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
    let sum = 0;
    let count = 0;

    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i += 1) {
      sum += buffer[i];
      count += 1;
    }

    result[offsetResult] = sum / count;
    offsetResult += 1;
    offsetBuffer = nextOffsetBuffer;
  }

  return result;
}

function floatTo16BitPCM(floatBuffer) {
  const output = new Int16Array(floatBuffer.length);
  for (let i = 0; i < floatBuffer.length; i += 1) {
    const s = Math.max(-1, Math.min(1, floatBuffer[i]));
    output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return output;
}

async function setupAudio() {
  mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  audioContext = new (window.AudioContext || window.webkitAudioContext)({
    sampleRate: TARGET_SAMPLE_RATE,
  });

  source = audioContext.createMediaStreamSource(mediaStream);
  processor = audioContext.createScriptProcessor(BUFFER_SIZE, 1, 1);

  processor.onaudioprocess = (event) => {
    const input = event.inputBuffer.getChannelData(0);
    const downsampled = downsampleBuffer(input, audioContext.sampleRate, TARGET_SAMPLE_RATE);
    const pcmChunk = floatTo16BitPCM(downsampled);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(pcmChunk.buffer);
    }
  };

  source.connect(processor);
  processor.connect(audioContext.destination);
}

function teardownAudio() {
  if (processor) {
    processor.disconnect();
    processor = null;
  }
  if (source) {
    source.disconnect();
    source = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
}

function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${protocol}://${window.location.host}/ws/transcribe`;

  ws = new WebSocket(wsUrl);
  ws.binaryType = "arraybuffer";

  ws.onopen = () => {
    setStatus("Live", true);
    meterText.textContent = "Listening...";
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "partial") {
      appendText(data.text, false);
    }
    if (data.type === "final") {
      appendText(data.text, true);
    }
    if (data.type === "error") {
      meterText.textContent = data.message || "Error receiving transcript.";
    }
  };

  ws.onclose = () => {
    setStatus("Idle", false);
    meterText.textContent = "Connection closed.";
  };
}

startBtn.addEventListener("click", async () => {
  startBtn.disabled = true;
  stopBtn.disabled = false;
  try {
    connectWebSocket();
    await setupAudio();
  } catch (err) {
    meterText.textContent = err.message || "Mic access failed.";
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
});

stopBtn.addEventListener("click", () => {
  stopBtn.disabled = true;
  startBtn.disabled = false;
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send("__flush__");
    ws.close();
  }
  teardownAudio();
  setStatus("Idle", false);
  meterText.textContent = "Stopped.";
});

clearBtn.addEventListener("click", () => {
  notes.value = "";
  lastUpdate.textContent = "Cleared.";
});

setStatus("Idle", false);
