from ProfileCreator.helpers.file_helper import clear_dir
from ProfileCreator.parsers.sensors_parser import SensorParser
from ProfileCreator.common.sensor_reading import SensorReading
import unittest
from datetime import datetime
from typing import List, Tuple
import os

class SensorParserTests(unittest.TestCase):

    def setUp(self):
        self._files_test_data = [
            "unittests/data/good_sensor_data_1.bin",
            "unittests/data/good_sensor_data_2.bin"
            #"data\\good_sensor_data_3.bin"
        ]

        with open(self.relativeFilename("unittests/data/readings_1.py")) as file:
            readings_1 = eval(file.read())
        
        with open(self.relativeFilename("unittests/data/readings_1.py")) as file:
            readings_2 = eval(file.read())
        
        with open(self.relativeFilename("unittests/data/readings_3.py")) as file:
            readings_3 = eval(file.read())

        self._readings_test_data = [
            readings_1,
            readings_2,
            readings_3
        ]

        self._empty_file = "unittests/data/empty.bin"
        self._eight_zeros_file = "unittests/data/eight_zeros.bin"
        self._eight_zeros_in_the_middle_file = "unittests/data/eight_zeros_in_the_middle.bin"
        self._no_eight_zeros_file = "unittests/data/no_eight_zeros.bin"
        self._incorrect_formating_file = "unittests/data/incorrect_formatting.bin"
        self._correct_config_file = "unittests/data/sensor_config.json"
        self._empty_config_file = "unittests/data/sensor_config_empty.json"
        self._config_no_acceleration_file = "unittests/data/sensor_config_no_acceleration.json"
        self._config_no_magnetic_field_file = "unittests/data/sensor_config_no_magnetic_field.json"
        self._config_no_gyroscope_file = "unittests/data/sensor_config_no_gyroscope.json"
        self._config_no_gravity_file = "unittests/data/sensor_config_no_gravity.json"
        self._config_no_linear_acceleration_file = "unittests/data/sensor_config_no_linear_acceleration.json"
        self._config_no_rotation_file = "unittests/data/sensor_config_no_rotation.json"
        self._temp_dir = "unittests/data/tmp"

        try:
            os.mkdir(self.relativeFilename(self._temp_dir))
        except FileExistsError:
            pass
        

    def tearDown(self):
        clear_dir(self.relativeFilename(self._temp_dir ))

    def tmpFilename(self) -> str:
        ret = os.path.join(self.relativeFilename(self._temp_dir), 
            datetime.now().strftime("%m%d%Y%H%M%S"))
        return ret
    
    def relativeFilename(self, filename: str) -> str:
        ret = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        return ret

    def test_binaryFile_ifWellFormated_isParsedAndSaved_correctly(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)

        for filename in self._files_test_data:
            with self.subTest():
                filename = self.relativeFilename(filename)
                with open(filename, 'rb') as file:
                    content = file.read()
                with open(filename, 'rb') as file:
                    readings = parser.parseFile(file)
                tmp_filename = self.tmpFilename()
                with open(tmp_filename, "wb") as file:
                    parser.writeFile(readings, file)
                with open(tmp_filename, "rb") as file:
                    self.assertEqual(content, file.read())

    def test_binaryData_ifWellFormated_isParsedAndRetrieved_correctly(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        for filename in self._files_test_data:
            with self.subTest():
                filename = self.relativeFilename(filename)
                with open(filename, 'rb') as file:
                    content = file.read()
                
                readings = parser.parseData(content)
                retrieved = parser.toBinary(readings)
                self.assertEqual(content, retrieved)

    def test_listOfSensorReadings_isSavedToFileAndRead_correctly(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        for readings in self._readings_test_data:
            with self.subTest():
                tmp_filename = self.tmpFilename()
                with open(tmp_filename, 'wb') as file:
                    parser.writeFile(readings, file)
                with open(tmp_filename, 'rb') as file:
                    readings_read = parser.parseFile(file)
                for (it1, it2) in zip(readings, readings_read):
                    self.assertTrue(it2.almostEqual(it1))

    def test_listOfSensorReadings_isFromattedAndRead_correctly(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        for readings in self._readings_test_data:
            with self.subTest():
                binary = parser.toBinary(readings)
                readings_read = parser.parseData(binary)
                for (it1, it2) in zip(readings, readings_read):
                    self.assertTrue(it2.almostEqual(it1))
    
    def test_parser_initializedWithEmptyText_throwsValueError(self):
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._empty_config_file)) as file:
                parser = SensorParser(file)

    def test_parser_initializedWithConfigWithoutAccelerationField_throwsValueError(self):
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._config_no_acceleration_file)) as file:
                parser = SensorParser(file)

    def test_parser_initializedWithConfigWithoutMagneticFieldField_throwsValueError(self):
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._config_no_magnetic_field_file)) as file:
                parser = SensorParser(file)

    def test_parser_initializedWithConfigWithoutGyroscopeField_throwsValueError(self):
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._config_no_gyroscope_file)) as file:
                parser = SensorParser(file)

    def test_parser_initializedWithConfigWithoutGravityField_throwsValueError(self):
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._config_no_gravity_file)) as file:
                parser = SensorParser(file)

    def test_parser_initializedWithConfigWithoutLinearAccelerationField_throwsValueError(self):
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._config_no_linear_acceleration_file)) as file:
                parser = SensorParser(file)

    def test_parser_initializedWithConfigWithoutRotationField_throwsValueError(self):
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._config_no_rotation_file)) as file:
                parser = SensorParser(file)

    def test_parser_readingFileNotInBinaryMode_throwsValueError(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._files_test_data[0]), "r") as file:
                parser.parseFile(file)

    def test_parser_readingEmptyFile_throwsValueError(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._empty_file), "rb") as file:
                parser.parseFile(file)

    def test_parser_readingFileWithOnlyEightZeros_returnsEmptyList(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        with open(self.relativeFilename(self._eight_zeros_file), "rb") as file:
            self.assertListEqual(parser.parseFile(file), [])

    def test_parser_readingFileWithEightZerosInTheMiddle_throwsValueError(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._eight_zeros_in_the_middle_file), "rb") as file:
            	parser.parseFile(file)

    def test_parser_readingFileWithoutEightZeros_throwsValueError(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._no_eight_zeros_file), "rb") as file:
            	parser.parseFile(file)

    def test_parser_readingFileWithIncorrectFormatting_throwsValueError(self):
        with open(self.relativeFilename(self._correct_config_file)) as file:
            parser = SensorParser(file)
        
        with self.assertRaises(ValueError):
            with open(self.relativeFilename(self._incorrect_formating_file), "rb") as file:
            	parser.parseFile(file)

if __name__ == '__main__':
    unittest.main()