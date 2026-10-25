"""Small checks for the standalone integration arithmetic."""

import math
import unittest
from types import SimpleNamespace

from imu_radial_guard.motion_math import MotionEstimate


def fake_orientation(yaw):
    return SimpleNamespace(x=0.0, y=0.0, z=math.sin(yaw / 2), w=math.cos(yaw / 2))


class MotionEstimateTests(unittest.TestCase):
    def test_constant_acceleration(self):
        m = MotionEstimate()
        q = fake_orientation(0.0)
        acceleration = SimpleNamespace(x=1.0, y=0.0)
        for second in (0.0, 1.0, 2.0):
            m.add_reading(second, q, acceleration)
        self.assertAlmostEqual(m.east, 3.0)
        self.assertAlmostEqual(m.north, 0.0)
        self.assertAlmostEqual(m.radius, 3.0)

    def test_yaw_turns_acceleration(self):
        m = MotionEstimate()
        q = fake_orientation(math.pi / 2)
        acceleration = SimpleNamespace(x=1.0, y=0.0)
        m.add_reading(0.0, q, acceleration)
        m.add_reading(1.0, q, acceleration)
        self.assertAlmostEqual(m.east, 0.0, places=6)
        self.assertAlmostEqual(m.north, 1.0, places=6)

    def test_repeated_timestamp_is_skipped(self):
        m = MotionEstimate()
        q = fake_orientation(0.0)
        acceleration = SimpleNamespace(x=1.0, y=0.0)
        m.add_reading(0.0, q, acceleration)
        m.add_reading(0.0, q, acceleration)
        self.assertEqual(m.radius, 0.0)


if __name__ == '__main__':
    unittest.main()
