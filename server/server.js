// server.js
const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
app.get('/', (req, res) => {
  res.send("CTF Remote WebSocket Server is running ✅");
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let robots = {};       // robotId -> ws
let clients = {};      // clientId -> ws
let supervisors = {};  // supervisorId -> ws

function broadcastToClients(msgObj) {
  const msg = JSON.stringify(msgObj);
  for (const id in clients) {
    const cws = clients[id];
    if (cws && cws.readyState === WebSocket.OPEN) {
      cws.send(msg);
    }
  }
}

wss.on('connection', (ws, req) => {
  console.log("🔗 New WebSocket connection from", req.socket.remoteAddress);

  ws.on('message', (raw) => {
    let data;
    try {
      data = JSON.parse(raw);
    } catch (err) {
      console.error("Invalid JSON:", err);
      return;
    }

    // Registration
    if (data.type === 'register') {
      if (data.role === 'robot') {
        robots[data.id] = ws;
        console.log("🤖 Robot registered:", data.id);
      } else if (data.role === 'client') {
        clients[data.id] = ws;
        console.log("🧑‍💻 Client registered:", data.id);
      } else if (data.role === 'supervisor') {
        supervisors[data.id] = ws;
        console.log("🧠 Supervisor registered:", data.id);
      }
      return;
    }

    // Control signal
    if (data.type === 'control') {
      if (robots[data.id] && robots[data.id].readyState === WebSocket.OPEN) {
        robots[data.id].send(JSON.stringify({
          type: 'control',
          vx: data.vx,
          wz: data.wz
        }));
      }
      return;
    }

    // Game event broadcast
    if (data.type === 'game_event') {
      console.log("🏁 Game event:", data);
      broadcastToClients(data);
      return;
    }

    console.log("Unhandled message:", data);
  });

  ws.on('close', () => {
    for (const id in robots) if (robots[id] === ws) delete robots[id];
    for (const id in clients) if (clients[id] === ws) delete clients[id];
    for (const id in supervisors) if (supervisors[id] === ws) delete supervisors[id];
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
