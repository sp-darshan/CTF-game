from controller import Robot
import websocket, threading, json, time

ROBOT_ID = "epuck1"
SERVER_URL = "ws://localhost:8080"

robot = Robot()
timestep = int(robot.getBasicTimeStep())

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

target_vx = 0.0
target_wz = 0.0
WHEEL_RADIUS = 0.0205
AXLE_LENGTH = 0.052
MAX_SPEED = 6.28  # rad/s, max motor velocity for e-puck

def on_message(ws, message):
    global target_vx, target_wz
    data = json.loads(message)
    if data.get("type") == "control":
        target_vx = data["vx"]
        target_wz = data["wz"]

def ws_thread():
    ws = websocket.WebSocketApp(
        SERVER_URL,
        on_message=on_message
    )
    ws.on_open = lambda ws: ws.send(json.dumps({"type": "register", "role": "robot", "id": ROBOT_ID}))
    ws.run_forever()

threading.Thread(target=ws_thread, daemon=True).start()

while robot.step(timestep) != -1:
    # Convert vx, wz to wheel speeds
    left_speed = (target_vx - target_wz * AXLE_LENGTH / 2.0) / WHEEL_RADIUS
    right_speed = (target_vx + target_wz * AXLE_LENGTH / 2.0) / WHEEL_RADIUS

    # Restrict wheel speeds within [-MAX_SPEED, MAX_SPEED]
    left_speed = max(min(left_speed, MAX_SPEED), -MAX_SPEED)
    right_speed = max(min(right_speed, MAX_SPEED), -MAX_SPEED)

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
