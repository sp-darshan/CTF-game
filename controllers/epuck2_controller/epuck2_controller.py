from controller import Robot
import websocket, threading, json

# ================= CONFIG =================
ROBOT_ID = "epuck2"
SERVER_URL = "wss://ctf-game-d6xx.onrender.com"  # Use your Render WebSocket URL here

# Robot parameters
WHEEL_RADIUS = 0.0205
AXLE_LENGTH = 0.052
MAX_SPEED = 6.28  # rad/s

# =========================================

robot = Robot()
timestep = int(robot.getBasicTimeStep())

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0)
right_motor.setVelocity(0)

# Target velocities
target_vx = 0.0
target_wz = 0.0

# ---------------- WebSocket Callbacks ----------------
def on_message(ws, message):
    """
    Handles incoming WebSocket messages from client UI.
    Adds reverse logic: negative vx moves backward.
    """
    global target_vx, target_wz
    data = json.loads(message)
    if data.get("type") == "control":
        vx = data.get("vx", 0)
        wz = data.get("wz", 0)
        # Reverse logic: negative vx -> backward
        target_vx = vx
        target_wz = wz

def ws_thread():
    ws = websocket.WebSocketApp(
        SERVER_URL,
        on_message=on_message
    )
    # Register as robot on server
    def on_open(ws):
        ws.send(json.dumps({"type": "register", "role": "robot", "id": ROBOT_ID}))
    ws.on_open = on_open
    ws.run_forever()

# Start WebSocket in background thread
threading.Thread(target=ws_thread, daemon=True).start()

# ---------------- Main Robot Loop ----------------
while robot.step(timestep) != -1:
    # Convert vx, wz to differential wheel speeds
    left_speed = (target_vx - target_wz * AXLE_LENGTH / 2.0) / WHEEL_RADIUS
    right_speed = (target_vx + target_wz * AXLE_LENGTH / 2.0) / WHEEL_RADIUS

    # Clamp wheel speeds to [-MAX_SPEED, MAX_SPEED]
    left_speed = max(min(left_speed, MAX_SPEED), -MAX_SPEED)
    right_speed = max(min(right_speed, MAX_SPEED), -MAX_SPEED)

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
