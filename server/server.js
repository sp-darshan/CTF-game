const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

let robots = {}; // { playerId: ws }
let clients = {}; // { clientId: ws }

wss.on('connection', (ws) => {
  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg);

      if (data.type === 'register') {
        // Register client or robot
        if (data.role === 'robot') robots[data.id] = ws;
        else if (data.role === 'client') clients[data.id] = ws;
      }

      if (data.type === 'control') {
        // Forward control to robot
        if (robots[data.id]) {
          robots[data.id].send(JSON.stringify({ type: 'control', vx: data.vx, wz: data.wz }));
        }
      }

    } catch (err) {
      console.error('Error:', err);
    }
  });

  ws.on('close', () => {
    for (let id in robots) if (robots[id] === ws) delete robots[id];
    for (let id in clients) if (clients[id] === ws) delete clients[id];
  });
});

console.log('WebSocket server running on ws://localhost:8080');
