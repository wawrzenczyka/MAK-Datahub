from ProfileCreator.common.event_reading import EventReading, EventType
from typing import BinaryIO
from typing import TextIO
import os
import datetime
class EventParser:
    def __init__(self):
        pass

    def parseFile(self, file: BinaryIO) -> List[EventReading]:
        if not is_opened_binary(file):
            raise ValueError("file is not opened as a binary stream")
        return parseData(file.read())

    def parseData(self, data: bytes) -> List[EventReading]:
        result = []
        if len(data) == 0:
            raise ValueError("Empty data is not correct")
        if ((len(data) - 8) % 12) != 0:
            raise ValueError("Incorrectly formatted data (wrong length)")
        expected_count = (len(data) - 8) / 12
        i = 0
        while True:
            bytes_timestamp = data[i*12, i*12+8]
            timestamp = int.from_bytes(bytes_timestamp, byteorder='big', signed=False)
            if timestamp == 0:
                break
            if i == expected_count:
                raise ValueError("Last timestamp was not 0")
            event_type = EventType(int.from_bytes(data[i*12 + 8, i*12 + 12]))
            result.append(EventReading(timestamp, event_type))
            i += 1
        if i < exected:
            raise ValueError("Encountered timestamp 0 in the middle of data")


    def writeFile(self, readings: List[EventReading], file: BinaryIO) -> None:
        if not is_opened_binary(file):
            raise ValueError("file is not opened as a binary stream")
        for reading in readings:
            file.write(reading.Timestamp.to_bytes(8, byteorder="big"))
            file.write(reading.EventType.value.to_bytes(4, byteorder="big"))
        file.write((0).to_bytes(8, byteorder="big"))

    def toBinary(self, readings: List[SensorReadings]) -> bytes:
        tmp_file = "tmp_%s" % datetime.timestamp(datetime.now())
        try:
            with open(tmp_file, "wb") as file:
                self.writeFile(self, readings, file)
            with open(tmp_file, "rb") as file:
                file.read()
        finally:
            os.remove(tmp_file)