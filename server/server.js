// server.js
const http = require('http');
const WebSocket = require('ws');

const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end("WebSocket server for CTF Remote");
});

const wss = new WebSocket.Server({ server });

let robots = {};     // robotId -> ws
let clients = {};    // clientId -> ws
let supervisors = {}; // optional

function broadcastToClients(msgObj) {
  const msg = JSON.stringify(msgObj);
  for (const id in clients) {
    const cws = clients[id];
    if (cws && cws.readyState === WebSocket.OPEN) {
      cws.send(msg);
    }
  }
}

wss.on('connection', (ws) => {
  ws.on('message', (raw) => {
    let data;
    try {
      data = JSON.parse(raw);
    } catch (err) {
      console.error("Invalid JSON:", err);
      return;
    }

    if (data.type === 'register') {
      if (data.role === 'robot') {
        robots[data.id] = ws;
        console.log("Robot registered:", data.id);
      } else if (data.role === 'client') {
        clients[data.id] = ws;
        console.log("Client registered:", data.id);
      } else if (data.role === 'supervisor') {
        supervisors[data.id] = ws;
        console.log("Supervisor registered:", data.id);
      }
      return;
    }

    if (data.type === 'control') {
      // forward control to robot if connected
      if (robots[data.id] && robots[data.id].readyState === WebSocket.OPEN) {
        robots[data.id].send(JSON.stringify({ type: 'control', vx: data.vx, wz: data.wz }));
      }
      return;
    }

    if (data.type === 'game_event') {
      // received from supervisor - broadcast to all clients
      console.log("Game event:", data);
      broadcastToClients(data);
      return;
    }

    // pass-through for debug
    console.log("Unhandled message:", data);
  });

  ws.on('close', () => {
    // remove from robots/clients/supervisors if matched
    for (const id in robots) if (robots[id] === ws) delete robots[id];
    for (const id in clients) if (clients[id] === ws) delete clients[id];
    for (const id in supervisors) if (supervisors[id] === ws) delete supervisors[id];
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
