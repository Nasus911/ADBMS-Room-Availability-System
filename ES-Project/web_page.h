#pragma once

// Single HTML page in PROGMEM
const char INDEX_HTML[] PROGMEM = R"HTML(
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ESP32 Web Lab</title>
<style>
:root{
  --bg:#0e1116; --card:#161b22; --text:#e6edf3; --muted:#8b949e;
  --ok:#2ea043; --bad:#f85149; --accent:#58a6ff;
}
*{box-sizing:border-box;font-family:"Trebuchet MS", Arial, sans-serif;}
body{margin:0;background:radial-gradient(circle at 20% 20%,#1c2330 0,#0e1116 60%);color:var(--text);}
header{padding:16px 20px;font-size:20px;font-weight:700;}
.grid{display:grid;gap:12px;padding:0 20px 20px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));}
.card{background:var(--card);border:1px solid #30363d;border-radius:14px;padding:16px;box-shadow:0 6px 24px rgba(0,0,0,.25);}
h2{margin:0 0 10px 0;font-size:16px;color:var(--muted);font-weight:600;}
.value{font-size:28px;font-weight:700;}
.bar{width:100%;height:12px;background:#0b0f14;border-radius:999px;overflow:hidden;border:1px solid #2d333b;}
.bar > span{display:block;height:100%;background:linear-gradient(90deg,#58a6ff,#2ea043);width:0%;}
.btns{display:flex;gap:10px;flex-wrap:wrap;}
button{background:#21262d;color:var(--text);border:1px solid #30363d;border-radius:10px;padding:10px 14px;cursor:pointer;}
button:hover{border-color:#58a6ff;}
.status{display:inline-block;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:700;}
.ok{background:rgba(46,160,67,.2);color:var(--ok);border:1px solid var(--ok);}
.bad{background:rgba(248,81,73,.2);color:var(--bad);border:1px solid var(--bad);}
small{color:var(--muted);}
</style>
</head>
<body>
<header>ESP32 Web Lab - Weight & Distance Test Bench</header>

<div class="grid">
  <div class="card">
    <h2>Connection</h2>
    <div id="conn" class="status bad">Disconnected</div>
    <div style="margin-top:10px"><small id="meta">...</small></div>
  </div>

  <div class="card">
    <h2>Weight (grams)</h2>
    <div class="value" id="weight">0.0</div>
    <div class="bar"><span id="wbar"></span></div>
  </div>

  <div class="card">
    <h2>Distance (cm)</h2>
    <div class="value" id="distance">0.0</div>
    <div class="bar"><span id="dbar"></span></div>
  </div>

  <div class="card">
    <h2>Actions</h2>
    <div class="btns">
      <button onclick="sendCmd('tare')">Tare Scale</button>
      <button onclick="sendCmd('calibrate')">Calibrate Weight</button>
      <button onclick="sendCmd('ping')">Ping Distance</button>
    </div>
    <div style="margin-top:8px"><small>OTA: /update | WebSerial: /webserial</small></div>
  </div>
</div>

<script>
let ws;
const conn = document.getElementById('conn');
const weightEl = document.getElementById('weight');
const distEl = document.getElementById('distance');
const wbar = document.getElementById('wbar');
const dbar = document.getElementById('dbar');
const meta = document.getElementById('meta');

function setConn(ok){
  conn.className = "status " + (ok ? "ok" : "bad");
  conn.textContent = ok ? "ESP32 Connected" : "Disconnected";
}
function connect(){
  ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onopen = ()=>setConn(true);
  ws.onclose = ()=>{setConn(false); setTimeout(connect, 1000);};
  ws.onmessage = (e)=>{
    try{
      const data = JSON.parse(e.data);
      if(data.weight !== undefined) weightEl.textContent = data.weight.toFixed(1);
      if(data.distance !== undefined) distEl.textContent = data.distance.toFixed(1);
      if(data.wbar !== undefined) wbar.style.width = data.wbar + "%";
      if(data.dbar !== undefined) dbar.style.width = data.dbar + "%";
      if(data.meta !== undefined) meta.textContent = data.meta;
    }catch(err){}
  };
}
function sendCmd(cmd){
  if(ws && ws.readyState === 1){
    ws.send(JSON.stringify({cmd}));
  }
}
connect();
</script>
</body>
</html>
)HTML";
