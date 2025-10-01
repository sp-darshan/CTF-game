const http = require('http');
const fs = require('fs');
const WebSocket = require('ws');

// HTTP server (optional, mainly for testing)
const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end("WebSocket server for CTF Remote");
});

// WebSocket server
const wss = new WebSocket.Server({ server });

let robots = {};
let clients = {};

wss.on('connection', (ws) => {
  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg);

      if (data.type === 'register') {
        if (data.role === 'robot') robots[data.id] = ws;
        else if (data.role === 'client') clients[data.id] = ws;
      }

      if (data.type === 'control') {
        if (robots[data.id]) {
          robots[data.id].send(JSON.stringify({
            type: 'control', vx: data.vx, wz: data.wz
          }));
        }
      }
    } catch (err) { console.error(err); }
  });

  ws.on('close', () => {
    for (let id in robots) if (robots[id] === ws) delete robots[id];
    for (let id in clients) if (clients[id] === ws) delete clients[id];
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
