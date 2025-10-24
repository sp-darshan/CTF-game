# flag_spawn_code.py
from controller import Supervisor
import threading, json, time, random
import numpy as np
try:
    import websocket
except Exception as e:
    print("websocket-client not available in this Python env. Install it if you want networked notifications.")
    websocket = None

# ----- CONFIG -----
SERVER_URL = "wss://ctf-game-d6xx.onrender.com"   # your render WS url
CAPTURE_DISTANCE = 0.06   # meters - when a robot is this close to flag -> capture
TIE_DISTANCE_DIFF = 0.02  # if distance difference < this => tie
RESPAWN_DELAY = 1.0       # seconds to wait after event before re-enabling
# -------------------

supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

# get nodes by DEF (you must add DEF EPUCK1 / DEF EPUCK2 in your .wbt)
flag_node = supervisor.getFromDef("FLAG")
epuck1_node = supervisor.getFromDef("EPUCK1")
epuck2_node = supervisor.getFromDef("EPUCK2")

if not flag_node or not epuck1_node or not epuck2_node:
    print("ERROR: Cannot find FLAG or EPUCK nodes. Make sure .wbt has DEF FLAG, DEF EPUCK1, DEF EPUCK2.")
    # still run but no network events
translation_field = flag_node.getField("translation")

# store robot translation and rotation fields to reset later
epuck1_trans_field = epuck1_node.getField("translation")
epuck1_rot_field = epuck1_node.getField("rotation")
epuck2_trans_field = epuck2_node.getField("translation")
epuck2_rot_field = epuck2_node.getField("rotation")

# store initial poses (so we can reset)
EPUCK1_INIT_POS = list(epuck1_trans_field.getSFVec3f())
EPUCK1_INIT_ROT = list(epuck1_rot_field.getSFRotation())
EPUCK2_INIT_POS = list(epuck2_trans_field.getSFVec3f())
EPUCK2_INIT_ROT = list(epuck2_rot_field.getSFRotation())

# Example possible flag spawn points (replace with your maze-chosen points later)
possible_points = [
    [0.35, -0.1, 0.0],
    [-0.3, +0.27, 0.0],
    [-0.1, -0.6, 0.0]
]

initial_flag_pos = possible_points[np.random.randint(0, len(possible_points))]
print(initial_flag_pos)

translation_field.setSFVec3f([
    initial_flag_pos[0],
    initial_flag_pos[1],
    initial_flag_pos[2] if len(initial_flag_pos) >= 3 else 0.05
])

last_spawn_index = 0

# Networking: open a websocket to notify server about game events
ws = None
ws_connected = False

def ws_on_open(w):
    global ws_connected
    ws_connected = True
    # register as supervisor
    try:
        w.send(json.dumps({"type": "register", "role": "supervisor", "id": "supervisor1"}))
    except Exception as e:
        print("Failed to register on server:", e)

def ws_on_close(w, *args):
    global ws_connected
    ws_connected = False
    print("Supervisor WS closed")

def ws_on_error(w, err):
    print("Supervisor WS error:", err)

def init_ws():
    global ws
    if websocket is None:
        return
    try:
        ws = websocket.WebSocketApp(SERVER_URL,
                                    on_open=ws_on_open,
                                    on_close=ws_on_close,
                                    on_error=ws_on_error)
        threading.Thread(target=ws.run_forever, daemon=True).start()
    except Exception as e:
        print("Supervisor failed to start WS thread:", e)

def broadcast_event(evt):
    """
    evt: dict, e.g. {"type":"game_event","event":"win","winner":"epuck1", ...}
    send to server if connected
    """
    global ws, ws_connected
    if ws and ws_connected:
        try:
            ws.send(json.dumps(evt))
        except Exception as e:
            print("Failed to send event:", e)
    else:
        # no ws -> just print
        print("GAME EVENT:", evt)

# helper: get world position of a node
def get_node_position(node):
    t = list(node.getField("translation").getSFVec3f())
    return t  # [x,y,z]

def distance2(a,b):
    dx = a[0]-b[0]; dy = a[1]-b[1]; dz = a[2]-b[2]
    return (dx*dx + dy*dy + dz*dz) ** 0.5

# initialize websocket connection
init_ws()

# small debounce so one capture only triggers once
game_locked = False
lock_timer = 0.0

print("Supervisor game manager started.")
while supervisor.step(timestep) != -1:
    # check timeouts
    if game_locked:
        lock_timer -= timestep/1000.0
        if lock_timer <= 0:
            game_locked = False

    # every step: read flag and robot positions
    flag_pos = get_node_position(flag_node)
    p1 = get_node_position(epuck1_node)
    p2 = get_node_position(epuck2_node)

    dist1 = distance2(p1, flag_pos)
    dist2 = distance2(p2, flag_pos)

    # if either robot within capture range and not locked, decide winner/tie
    if not game_locked and (dist1 <= CAPTURE_DISTANCE or dist2 <= CAPTURE_DISTANCE):
        # compute result
        if abs(dist1 - dist2) <= TIE_DISTANCE_DIFF:
            result = "tie"
            payload = {"type":"game_event","event":"tie","details":{"dist1":dist1,"dist2":dist2,"flag":flag_pos}}
            print("TIE detected:", dist1, dist2)
        elif dist1 < dist2:
            result = "epuck1"
            payload = {"type":"game_event","event":"win","winner":"epuck1","details":{"dist1":dist1,"dist2":dist2,"flag":flag_pos}}
            print("EPUCK1 wins")
        else:
            result = "epuck2"
            payload = {"type":"game_event","event":"win","winner":"epuck2","details":{"dist1":dist1,"dist2":dist2,"flag":flag_pos}}
            print("EPUCK2 wins")

        # send event to server (server will broadcast to clients)
        broadcast_event(payload)

        # lock game loop briefly
        game_locked = True
        lock_timer = RESPAWN_DELAY

        # Reset: respawn flag and teleport robots back to initial spots after a tiny delay
        # pick next spawn point
        new_flag_pos = possible_points[np.random.randint(0, len(possible_points))]

        # set flag translation (keep small positive Z to sit above floor)
        new_flag_pos_with_z = [
            new_flag_pos[0], 
            new_flag_pos[1], 
            new_flag_pos[2] if len(new_flag_pos) >= 3 else 0.05
        ]
        
        translation_field.setSFVec3f(new_flag_pos_with_z)

        # reset robots to initial pose
        epuck1_trans_field.setSFVec3f(EPUCK1_INIT_POS)
        epuck1_rot_field.setSFRotation(EPUCK1_INIT_ROT)
        epuck2_trans_field.setSFVec3f(EPUCK2_INIT_POS)
        epuck2_rot_field.setSFRotation(EPUCK2_INIT_ROT)

        # small delay to avoid immediate re-trigger
        # use supervisor.step loop with game_locked flag; we already set lock_timer

    # continue simulation
