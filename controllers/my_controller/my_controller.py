"""my_controller controller."""

from controller import Robot, Motor, DistanceSensor

# Create the Robot instance
robot = Robot()

# Get the time step of the current world
timestep = int(robot.getBasicTimeStep())

# Get and enable distance sensors (assuming e-puck with 8 sensors)
sensor_names = [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4', 'ps5', 'ps6', 'ps7'
]
sensors = []
for name in sensor_names:
    ds = robot.getDevice(name)
    ds.enable(timestep)
    sensors.append(ds)

# Get motors
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')

# Set motors to velocity control mode
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Max speed for e-puck motors
MAX_SPEED = 6.28

# Main loop
while robot.step(timestep) != -1:
    # Read sensor values
    sensor_values = [ds.getValue() for ds in sensors]

    # Default: go forward
    left_speed = MAX_SPEED
    right_speed = MAX_SPEED

    # Simple obstacle avoidance rule
    # If obstacle on the right → turn left
    if sensor_values[0] > 80 or sensor_values[1] > 80 or sensor_values[2] > 80:
        left_speed = -0.5 * MAX_SPEED
        right_speed = 0.5 * MAX_SPEED
    # If obstacle on the left → turn right
    elif sensor_values[5] > 80 or sensor_values[6] > 80 or sensor_values[7] > 80:
        left_speed = 0.5 * MAX_SPEED
        right_speed = -0.5 * MAX_SPEED

    # Apply motor speeds
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
