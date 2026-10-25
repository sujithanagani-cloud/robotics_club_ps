"""Drive straight until the IMU-based distance estimate reaches a limit."""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu

from .motion_math import MotionEstimate


class RadialGuard(Node):
    def __init__(self):
        super().__init__('radial_guard')

        self.declare_parameter('distance_limit', 10.0)
        self.declare_parameter('forward_speed', 0.2)
        self.limit = float(self.get_parameter('distance_limit').value)
        self.speed = float(self.get_parameter('forward_speed').value)

        self.tracker = MotionEstimate()
        self.done = False

        self.create_subscription(Imu, '/imu', self.on_imu, qos_profile_sensor_data)
        self.velocity_topic = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_timer(0.1, self.drive)

    def on_imu(self, message):
        if self.done:
            return

        t = message.header.stamp.sec + message.header.stamp.nanosec * 1e-9
        self.tracker.add_reading(t, message.orientation, message.linear_acceleration)
        if self.tracker.radius >= self.limit:
            self.done = True
            self.get_logger().info('Reached the estimated limit; stopping.')
            self.publish_stop()

    def publish_stop(self):
        self.velocity_topic.publish(Twist())

    def drive(self):
        command = Twist()
        if not self.done:
            command.linear.x = self.speed
        self.velocity_topic.publish(command)
        self.get_logger().info(f'Distance from IMU: {self.tracker.radius:.2f} m')


def main(args=None):
    rclpy.init(args=args)
    node = RadialGuard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
