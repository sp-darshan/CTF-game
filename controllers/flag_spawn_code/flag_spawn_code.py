from controller import Supervisor
import random

supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

# Get the FLAG node
flag = supervisor.getFromDef("FLAG")
translation_field = flag.getField("translation")

# Arena bounds
possible_points = [[0,0,0], [0.135,0.135,0], 
                   [-0.4, 0.135, 0]]
Y = 0.1   # height above ground
i=0
print(possible_points[i])
while supervisor.step(timestep) != -1:
    # Example: Respawn every 200 steps
    if supervisor.getTime() % 5 < 0.05:   # every ~5 seconds
        print(possible_points[i%3])
        translation_field.setSFVec3f(possible_points[i%3])
        print(f"Flag respawned at: {possible_points[i%3]}")
        i+=1