# Capture the Flag (CTF) Simulation Game

## Overview

This project implements a multi-robot **Capture the Flag** simulation using **Webots** and **Node.js**.  
Autonomous robots navigate within a simulated world to capture the opponent's flag and return it to their base.  
Communication between the robots and the central server is handled in real time via **WebSockets**.

The main components of the project include:
- **Webots** for robot simulation and environment setup.
- **Node.js WebSocket server** for managing game events and state.
- **Render** hosting for online multiplayer or remote access.

---

## Hosted

Frontend : https://ctf-game-taupe.vercel.app/

Backend : https://ctf-game-d6xx.onrender.com/

---

## Features

- Real-time communication between Webots robots and a Node.js server.
- Autonomous robot movement and flag capture logic.
- Centralized game control using WebSocket messages in JSON format.
- Configurable world environment and robot spawn points.
- Hosted multiplayer support via Render.

---

## System Architecture

The system is organized as follows:

1. Each robot runs a Python controller script in Webots.
2. The controller connects to the Node.js WebSocket server.
3. Robots send position and status data to the server at regular intervals.
4. The server validates capture events and broadcasts updates to all clients.
5. The simulation continues until one team successfully captures the flag.

---

## Folder Structure

```plaintext
ctf-game/
│
├── client/                # web interface 
├── controller/            # Webots robot controllers
│   ├── flag_spawn_code.py # Flag placement and respawn logic
│   ├── epuck1.py          # Robot 1 controller
│   ├── epuck2.py          # Robot 2 controller
│  
│
├── server/                # Node.js WebSocket server files
│   ├── server.js          # Main server logic
│   ├── package.json       # Server dependencies
│   
│
├── worlds/                # Webots world definitions
│   ├── capture_the_flag.wbt
│ 
│
└── README.md              # Project documentation


