from typing import List

class SensorReading:

    allowedError = 0.0001

    def __init__(self, timestamp: int, acceleration: List[float], magneticField: List[float], gyroscope: List[float],
      gravity: List[float], linearAcceleration: List[float], rotation: List[float]):
        self.Timestamp = timestamp
        self.Acceleration = acceleration
        self.MagneticField = magneticField
        self.Gyroscope = gyroscope
        self.Gravity = gravity
        self.LinearAcceleration = linearAcceleration
        self.Rotation = rotation

    def __eq__(self, other): 
        if not isinstance(other, SensorReading):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.Timestamp == other.Timestamp and \
            self.Acceleration == other.Acceleration and \
            self.MagneticField == other.MagneticField and \
            self.Gyroscope == other.Gyroscope and \
            self.Gravity == other.Gravity and \
            self.LinearAcceleration == other.LinearAcceleration and \
            self.Rotation == other.Rotation

    def __hash__(self):
        return hash((self.Timestamp, self.Gravity, self.MagneticField, self.Gyroscope,
            self.Gravity, self.LinearAcceleration, self.Rotation))

    def almostEqual(self, other):
        if not isinstance(other, SensorReading):
            # don't attempt to compare against unrelated types
            return NotImplemented

        l1 = self.Acceleration + self.MagneticField + self.Gyroscope + \
            self.Gravity + self.LinearAcceleration + self.Rotation
        
        l2 = other.Acceleration + other.MagneticField + other.Gyroscope + \
            other.Gravity + other.LinearAcceleration + other.Rotation

        if self.Timestamp != other.Timestamp:
            return False

        for (it1, it2) in zip(l1,l2):
            if abs(it1 - it2) > self.allowedError:
                return False

        return True