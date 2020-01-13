from ..common.event_reading import EventReading, EventType
from ..helpers.file_helper import is_opened_binary
from typing import BinaryIO, TextIO, List
import os
from datetime import datetime
class EventParser:
    def __init__(self):
        pass

    def parseFile(self, file: BinaryIO) -> List[EventReading]:
        if not is_opened_binary(file):
            raise ValueError("file is not opened as a binary stream")
        return self.parseData(file.read())

    def parseData(self, data: bytes) -> List[EventReading]:
        result = []
        if len(data) == 0:
            raise ValueError("Empty data is not correct")
        data_over_count = (len(data) - 8) % 12
        eight_zeros_version = False
        if data_over_count != 0:
            if data_over_count == 8:
                eight_zeros_version = True
            else:
                raise ValueError("Incorrectly formatted data (wrong length)")
        if eight_zeros_version:
            expected_count = (len(data) - 16) // 12
        else:
            expected_count = (len(data) - 8) // 12
        i = 0
        while True:
            bytes_timestamp = data[(i*12):(i*12+8)]
            timestamp = int.from_bytes(bytes_timestamp, byteorder='big', signed=False)
            if timestamp == 0:
                break
            if i == expected_count:
                raise ValueError("Last timestamp was not 0")
            event_type = EventType(int.from_bytes(data[(i*12 + 8):(i*12 + 12)], byteorder='big', signed=False))
            result.append(EventReading(timestamp, event_type))
            i += 1
        if i < expected_count:
            raise ValueError("Encountered timestamp 0 in the middle of data")
        if eight_zeros_version:
            bytes_timestamp = data[-8:]
            val = int.from_bytes(bytes_timestamp, byteorder='big', signed=False)
            if val != 0:
                raise ValueError("Eight last additional bytes are not 8")
        return result


    def writeFile(self, readings: List[EventReading], file: BinaryIO) -> None:
        if not is_opened_binary(file):
            raise ValueError("file is not opened as a binary stream")
        for reading in readings:
            file.write(reading.Timestamp.to_bytes(8, byteorder="big"))
            file.write(reading.EventType.value.to_bytes(4, byteorder="big"))
        file.write((0).to_bytes(8, byteorder="big"))

    def toBinary(self, readings: List[EventReading]) -> bytes:
        tmp_file = "tmp_%s" % datetime.now().strftime("%m%d%Y%H%M%S")
        try:
            with open(tmp_file, "wb") as file:
                self.writeFile(readings, file)
            with open(tmp_file, "rb") as file:
                return file.read()
        finally:
            try:
                os.remove(tmp_file)
            except Exception:
                pass