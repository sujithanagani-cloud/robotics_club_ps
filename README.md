# IMU radial guard

A small ROS 2 experiment in Gazebo. The robot drives forward, estimates how far it has moved from IMU readings, and sends a stop command when the **estimated distance from its starting point** reaches 10 m.

This is intentionally a basic solution. It does not use GPS, wheel odometry, or any localization package to decide when to stop.

## The idea

I split the code into two parts because it made it easier to follow:

- `motion_math.py` keeps track of estimated x/y velocity and position.
- `runner.py` handles the ROS 2 topics and tells the robot to move or stop.

The node listens to `/imu` and publishes to `/cmd_vel`. Every IMU message has a timestamp. I use the change in timestamp (`dt`) to update the estimate. Since the robot is on a flat surface, I use the IMU's yaw angle to express the horizontal accelerations in the world frame.

The updates are basically:

```text
velocity_x += acceleration_x * dt
velocity_y += acceleration_y * dt
position_x += velocity_x * dt
position_y += velocity_y * dt
radial_distance = sqrt(position_x**2 + position_y**2)
```

The target radius is 10 m, and the forward command is 0.2 m/s. Both numbers can be changed using ROS parameters. Once the estimate crosses the target, the node keeps publishing zero velocity. I also stop updating the position estimate after that point so the output doesn't keep drifting while stationary.

## Folder contents

```text
imu_radial_guard/
  README.md
  package.xml
  setup.py
  setup.cfg
  resource/
  imu_radial_guard/
    motion_math.py
    runner.py
  tests/
    test_motion_math.py
```

## How to run it

These instructions assume ROS 2 Humble, Gazebo Classic, and the TurtleBot3 Burger Gazebo model are installed in Ubuntu.

Put this folder inside `~/ros2_ws/src/` and build:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --packages-select imu_radial_guard
source install/setup.bash
```

**Terminal 1: Gazebo server**

```bash
source /opt/ros/humble/setup.bash
gzserver --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so
```

**Terminal 2: spawn a robot**

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 run gazebo_ros spawn_entity.py -entity burger -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf -x 0 -y 0 -z 0.01
```

**Terminal 3: start the distance stopper**

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run imu_radial_guard radial_guard
```

It prints the current IMU-estimated distance every 0.1 seconds. If you want to use a different target, for example 8 m:

```bash
ros2 run imu_radial_guard radial_guard --ros-args -p distance_limit:=8.0
```

To evaluate actual simulated motion, check `/odom` **before** starting the node and **after** it stops:

```bash
ros2 topic echo /odom --once
```

`/odom` is only for comparing the results. **It is not used anywhere in the controller or the stop decision.**

## Results / what I observed

I tested the program in Gazebo with the TurtleBot3 Burger robot. The robot started near the origin and moved forward until the IMU-estimated distance reached 10 metres.

The readings from the test were:

Measurement

Value

Target distance

10.00 m

IMU estimate when stopped

10.00 m

Starting odometry (x, y)

(0.00006532, -0.00000460) m

Final odometry (x, y)

(4.56969060, -0.00008558) m

Displacement calculated from odometry

4.5696 m

Error compared to target

5.4304 m

Percentage error

54.30%

Observations

The robot stopped once the IMU distance reached the specified limit, which shows that the stopping condition was working.

However, there was a noticeable difference between the estimated distance and the odometry reading. The actual displacement was around 4.57 metres, much less than the intended 10 metres.

I used acceleration values from the IMU to calculate velocity and then position. The problem with this approach is that small errors in acceleration accumulate over time, leading to a large difference in the estimated position.

The program successfully implements the basic IMU-based stopping logic, but the position estimation would need improvements to achieve a more accurate stopping distance.

## Limitations

The big problem is IMU drift. Any small bias in acceleration gets integrated into velocity, and then integrated again into position. That error can become pretty large even when the robot's motion looks simple. This implementation also uses yaw only, which assumes the robot stays more or less level. It isn't meant to be a precision tracking system.

The code also assumes the IMU orientation is usable and acceleration is in the expected frame. I would check those carefully before running it on real hardware.

## Quick checks

To check the math module without starting ROS or Gazebo, run this from the package folder:

```bash
python3 -m unittest discover -s tests
```

These tests only check the arithmetic; they do not replace a Gazebo test.


<img width="1600" height="832" alt="image_1" src="https://github.com/user-attachments/assets/3426b179-6937-4045-9a17-c91914e842d4" />

<img width="1600" height="895" alt="image_2" src="https://github.com/user-attachments/assets/bada9f24-9b4f-4917-9e27-f04dfcb7a5d4" />

<img width="1600" height="851" alt="image_3" src="https://github.com/user-attachments/assets/45d15fab-875c-4e3a-b8c7-2fe786e49df5" />.
