"""Very simple planar motion estimate using IMU readings only."""

from math import atan2, cos, hypot, sin


class MotionEstimate:
    def __init__(self):
        self.east = 0.0
        self.north = 0.0
        self.east_speed = 0.0
        self.north_speed = 0.0
        self.last_stamp = None

    @property
    def radius(self):
        return hypot(self.east, self.north)

    def add_reading(self, stamp, quaternion, acceleration):
        """Integrate one IMU reading using its timestamp.

        Quaternion and acceleration come directly from sensor_msgs/Imu.
        Uses only yaw, which assumes approximately level ground.
        """
        if self.last_stamp is None:
            self.last_stamp = stamp
            return

        delta_t = stamp - self.last_stamp
        self.last_stamp = stamp
        if delta_t <= 0:
            return

        # Turn the sensor's heading into a planar rotation.
        yaw = atan2(
            2 * (quaternion.w * quaternion.z + quaternion.x * quaternion.y),
            1 - 2 * (quaternion.y ** 2 + quaternion.z ** 2),
        )
        c, s = cos(yaw), sin(yaw)
        horizontal_x = acceleration.x * c - acceleration.y * s
        horizontal_y = acceleration.x * s + acceleration.y * c

        # First acceleration -> velocity, then velocity -> position.
        self.east_speed += horizontal_x * delta_t
        self.north_speed += horizontal_y * delta_t
        self.east += self.east_speed * delta_t
        self.north += self.north_speed * delta_t
