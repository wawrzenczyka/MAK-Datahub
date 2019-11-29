from ProfileCreator.helpers.file_helper import is_opened_binary
from ProfileCreator.common.sensor_reading import SensorReading
import json
from typing import BinaryIO
from typing import TextIO
import datetime
import os

class SensorParser:
    int4_max = 2**31 - 1 
    def __init__(self, config_json: TextIO):
        try:
            config = json.load(config_json)
            self.limits = config["limits"]
        except:
            raise ValueError("JSON is not valid")
        if not(len(self.limits != 6) and
          "acceleration" in self.limits and
          "magneticField" in self.limits and
          "gyroscope" in self.limits and
          "gravity" in self.limits and
          "linearAcceleration" in self.limits and
          "rotation" in self.limits):
            raise ValueError("Limits are not set correctly")

    def parseFile(self, file: BinaryIO) -> List[SensorReading]:
        if not is_opened_binary(file):
            raise ValueError("file is not opened as a binary stream")
        return parseData(file.read())

    def parseData(self, data: bytes) -> List[SensorReadings]:
        result = []
        if len(data) == 0:
            raise ValueError("Empty data is not correct")
        if ((len(data) - 8) % 80) != 0:
            raise ValueError("Incorrectly formatted data (wrong length)")
        expected_count = (len(data) - 8) / 80
        i = 0
        while True:
            bytes_timestamp = data[i*80, i*80+8]
            timestamp = int.from_bytes(bytes_timestamp, byteorder='big', signed=False)
            if timestamp == 0:
                break
            if i == expected_count:
                raise ValueError("Last timestamp was not 0")
            ints = [int.from_bytes(data[i*80 + 8 + j*4, i*80 + 8 + (j+1)*4], byteorder='big', signed=True) 
                for j in range(18)]
            acceleration = [float(x)*limits["acceleration"]/int4_max for x in ints[0:3]]
            magneticField = [float(x)*limits["magneticField"]/int4_max for x in ints[3:6]]            
            gyroscope = [float(x)*limits["gyroscope"]/int4_max for x in ints[6:9]]            
            gravity = [float(x)*limits["gravity"]/int4_max for x in ints[9:12]]
            linearAcceleration = [float(x)*limits["linearAcceleration"]/int4_max for x in ints[12:15]]
            rotation = [float(x)*limits["rotation"]/int4_max for x in ints[15:18]]
            result.append(SensorReading(timestamp, acceleration, magneticField, gyroscope, gravity,
                linearAcceleration, rotation))
            i += 1
        if i < exected:
            raise ValueError("Encountered timestamp 0 in the middle of data")


    def writeFile(self, readings: List[SensorReadings], file: BinaryIO) -> None:
        if not is_opened_binary(file):
            raise ValueError("file is not opened as a binary stream")
        for reading in readings:
            file.write(reading.Timestamp.to_bytes(8, byteorder="big"))
            for x in reading.Acceleration:
                file.write(int(x*int4_max/limits["acceleration"])(4, byteorder="big"))
            for x in reading.MagneticField:
                file.write(int(x*int4_max/limits["magneticField"])(4, byteorder="big"))
            for x in reading.Gyroscope:
                file.write(int(x*int4_max/limits["gyroscope"])(4, byteorder="big"))
            for x in reading.Gravity:
                file.write(int(x*int4_max/limits["gravity"])(4, byteorder="big"))
            for x in reading.LinearAcceleration:
                file.write(int(x*int4_max/limits["linearAcceleration"])(4, byteorder="big"))
            for x in reading.Rotation:
                file.write(int(x*int4_max/limits["rotation"])(4, byteorder="big"))
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