from ..helpers.file_helper import is_opened_binary
from ..common.sensor_reading import SensorReading
import json
from typing import BinaryIO, TextIO, List
from datetime import datetime
import os

class SensorParser:
    int4_max = 2**31 - 1 
    v1_offset = 0x0800000000000000
    def __init__(self, config_json_path: str):
        with open(config_json_path) as config_json:
            try:
                #config = json.load(config_json)
                config = json.load(config_json_path)
                self.limits = config["limits"]
            except:
                raise ValueError("JSON is not valid")
            if "acceleration" not in self.limits:
                raise ValueError("Limits are not set correctly - acceleration missing")
            if "magneticField" not in self.limits:
                raise ValueError("Limits are not set correctly - magneticField missing")
            if "gyroscope" not in self.limits:
                raise ValueError("Limits are not set correctly - gyroscope missing")
            if "gravity" not in self.limits:
                raise ValueError("Limits are not set correctly - gravity missing")
            if "linearAcceleration" not in self.limits:
                raise ValueError("Limits are not set correctly - linearAcceleration missing")
            if "rotation" not in self.limits:
                raise ValueError("Limits are not set correctly - rotation missing")

    def parseFile(self, file: BinaryIO) -> List[SensorReading]:
        # if not is_opened_binary(file):
        #     raise ValueError("file is not opened as a binary stream")
        return self.parseData(file.read())

    def parseData(self, data: bytes) -> List[SensorReading]:
        result = []
        if len(data) == 0:
            raise ValueError("Empty data is not correct")
        if ((len(data) - 8) % 80) != 0:
            raise ValueError("Incorrectly formatted data (wrong length)")
        expected_count = (len(data) - 8) / 80
        i = 0
        np = True
        while True:
            bytes_timestamp = data[i*80:i*80+8]
            timestamp = int.from_bytes(bytes_timestamp, byteorder='big', signed=False)
            if timestamp == 0:
                break
            if i == expected_count:
                raise ValueError("Last timestamp was not 0")
            ints = [int.from_bytes(data[(i*80 + 8 + j*4):(i*80 + 8 + (j+1)*4)], byteorder='big', signed=True) 
                for j in range(18)]
            acceleration = [float(x)*self.limits["acceleration"]/self.int4_max for x in ints[0:3]]
            magneticField = [float(x)*self.limits["magneticField"]/self.int4_max for x in ints[3:6]]            
            gyroscope = [float(x)*self.limits["gyroscope"]/self.int4_max for x in ints[6:9]]            
            gravity = [float(x)*self.limits["gravity"]/self.int4_max for x in ints[9:12]]
            linearAcceleration = [float(x)*self.limits["linearAcceleration"]/self.int4_max for x in ints[12:15]]
            rotation = [float(x)*self.limits["rotation"]/self.int4_max for x in ints[15:18]]
            if timestamp < self.v1_offset:
                magneticField = [x*self.limits["acceleration"]/self.limits["magneticField"] for x in magneticField]
                gyroscope = [x*self.limits["acceleration"]/self.limits["gyroscope"] for x in gyroscope]
                rotation = [x*self.limits["acceleration"]/self.limits["rotation"] for x in rotation]
            else:
                timestamp -= self.v1_offset
            result.append(SensorReading(timestamp, acceleration, magneticField, gyroscope, gravity,
                linearAcceleration, rotation))
            i += 1
        if i < expected_count:
            raise ValueError("Encountered timestamp 0 in the middle of data")
        return result


    def writeFile(self, readings: List[SensorReading], file: BinaryIO) -> None:
        if not is_opened_binary(file):
            raise ValueError("file is not opened as a binary stream")
        for reading in readings:
            file.write((reading.Timestamp + self.v1_offset).to_bytes(8, byteorder="big"))
            for x in reading.Acceleration:
                file.write(int(x*self.int4_max/self.limits["acceleration"]).to_bytes(4, byteorder="big", signed=True))
            for x in reading.MagneticField:
                file.write(int(x*self.int4_max/self.limits["magneticField"]).to_bytes(4, byteorder="big", signed=True))
            for x in reading.Gyroscope:
                file.write(int(x*self.int4_max/self.limits["gyroscope"]).to_bytes(4, byteorder="big", signed=True))
            for x in reading.Gravity:
                file.write(int(x*self.int4_max/self.limits["gravity"]).to_bytes(4, byteorder="big", signed=True))
            for x in reading.LinearAcceleration:
                file.write(int(x*self.int4_max/self.limits["linearAcceleration"]).to_bytes(4, byteorder="big", signed=True))
            for x in reading.Rotation:
                file.write(int(x*self.int4_max/self.limits["rotation"]).to_bytes(4, byteorder="big", signed=True))
        file.write((0).to_bytes(8, byteorder="big"))

    def toBinary(self, readings: List[SensorReading]) -> bytes:
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

    def fixThisReading(reading: SensorReading) -> None:
        reading.MagneticField = [x*self.limits["acceleration"]/self.limits["magneticField"] for x in reading.MagneticField]
        reading.Gyroscope = [x*self.limits["acceleration"]/self.limits["gyroscope"] for x in reading.Gyroscope]
        reading.Rotation = [x*self.limits["acceleration"]/self.limits["rotation"] for x in reading.Rotation]