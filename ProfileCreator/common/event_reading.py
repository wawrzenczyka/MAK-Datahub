from enum import Enum

class EventType(Enum):
    TOUCH = 0
    SCREEN_ON = 1
    SCREEN_OFF = 2
    UNLOCKED = 3
    UNLOCKED_BIOMETRICALLY = 4

class EventReading:
    def __init__(self, timestamp: int, eventType: EventType):
        self.Timestamp = timestamp
        self.EventType = eventType

    def __eq__(self, other): 
        if not isinstance(other, EventReading):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.Timestamp == other.Timestamp and \
            self.EventType == other.EventType

    def __hash__(self):
        return hash((self.Timestamp, self.Gravity, self.MagneticField, self.Gyroscope,
            self.Gravity, self.LinearAcceleration, self.Rotation))