from django.test import TestCase

from .models import Device
from .services.device_service import DeviceService

# DeviceService
class DeviceServiceTestCase(TestCase):
    def setUp(self):
        self.device_service = DeviceService()
        Device.objects.create(id = '1', token = '1234')
        Device.objects.create(id = '2', token = '2345')

    # get_device

    def test_GetDevice_WithNonStringID_ThrowsAssertionError(self):
        device_id = 1
        
        with self.assertRaises(AssertionError):
            self.device_service.get_device(device_id)

    def test_GetDevice_WithNonExistentID_ReturnsNone(self):
        device_id = 'invalid'

        device = self.device_service.get_device(device_id)

        self.assertIsNone(device)

    def test_GetDevice_WithValidID_ReturnsCorrectDeviceObject(self):
        device_id = '1'

        device = self.device_service.get_device(device_id)

        self.assertIsInstance(device, Device)
        self.assertEqual(device.id, device_id)

    # create_device

    def test_CreateDevice_WithNonStringID_ThrowsAssertionError(self):
        device_id = 1

        with self.assertRaises(AssertionError):
            self.device_service.create_device(device_id)

    def test_CreateDevice_WithNewID_CreatesDeviceInDatabase(self):
        device_id = '4'

        device = self.device_service.create_device(device_id)

        self.assertTrue(Device.objects.filter(id = device_id).exists())

    def test_CreateDevice_WithNewID_ReturnsCreatedDeviceInstance(self):
        device_id = '4'

        device = self.device_service.create_device(device_id)

        self.assertIsInstance(device, Device)
        self.assertEqual(device.id, device_id)
        self.assertIsNotNone(device.token)


    def test_CreateDevice_WithDuplicateID_RaisesValueError(self):
        device_id = '1'

        with self.assertRaises(ValueError):
            self.device_service.create_device(device_id)

from .models import DataFile
from .services.data_file_service import DataFileService
from .services.google_drive_service import GoogleDriveService

import pytz, datetime
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from unittest.mock import MagicMock

# DataFileService
class DataFileServiceTestCase(TestCase):
    def setUp(self):
        self.mockDevice = Device(id = '1', token = '1234')
        self.mockDevice.save()

        self.mockDataFile1 = DataFile(id = 1, file_uri = "drive_id_1", device = self.mockDevice, file_type = 'S', \
            start_date = datetime.datetime(2013, 11, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.mockDataFile2 = DataFile(id = 2, file_uri = "drive_id_2", device = self.mockDevice, file_type = 'E', \
            start_date = datetime.datetime(2019, 1, 1, 12, 0, 0, 0, tzinfo=pytz.UTC))

        self.mockDataFile1.save()
        self.mockDataFile2.save()

        self.file_storage_service = GoogleDriveService()
        self.file_storage_service.save_form_file = MagicMock(return_value = 'sample_drive_id')
        self.file_storage_service.get_file = MagicMock(return_value = 'sample_file_content')

        self.data_file_service = DataFileService(self.file_storage_service)
    
    # get_data_file_list
    def test_GetDataFileList_WhenCalled_ReturnsAllDataFilesFromDatabase(self):
        data_files = self.data_file_service.get_data_file_list()

        self.assertCountEqual(data_files, [self.mockDataFile1, self.mockDataFile2])

    # get_data_file
    def test_GetDataFile_WhenCalledWithNonIntID_ThrowsAssertionError(self):
        data_file_id = '1'

        with self.assertRaises(AssertionError):
            self.data_file_service.get_data_file(data_file_id)

    def test_GetDataFile_WhenCalledWithNonExistentID_ReturnsNone(self):
        data_file_id = 39

        data_file = self.data_file_service.get_data_file(data_file_id)

        self.assertIsNone(data_file)

    def test_GetDataFile_WhenCalledWithExistingID_ReturnsCorrectDataFile(self):
        data_file_id = 1

        data_file = self.data_file_service.get_data_file(data_file_id)

        self.assertIsInstance(data_file, DataFile)
        self.assertEqual(data_file, self.mockDataFile1)
        
    # create_data_file
    def test_CreateDataFile_WhenCalledWithIncorrectParameterType_ThrowsAssertionError(self):
        correct_file_data = TemporaryUploadedFile(content_type = 'text/text', size = 0, charset = 'UTF-8', name = 'file.txt')
        correct_device = self.mockDevice
        correct_start_date = datetime.datetime(2016, 2, 2, 1, 0, 0, 0, tzinfo=pytz.UTC)
        correct_file_type = 'S'
        
        incorrect_file_data = 1
        incorrect_device = 1
        incorrect_start_date = 1
        incorrect_file_type = 1

        with self.assertRaises(AssertionError):
            self.data_file_service.create_data_file(incorrect_file_data, correct_device, correct_start_date, correct_file_type)
        with self.assertRaises(AssertionError):
            self.data_file_service.create_data_file(correct_file_data, incorrect_device, correct_start_date, correct_file_type)
        with self.assertRaises(AssertionError):
            self.data_file_service.create_data_file(correct_file_data, correct_device, incorrect_start_date, correct_file_type)
        with self.assertRaises(AssertionError):
            self.data_file_service.create_data_file(correct_file_data, correct_device, correct_start_date, incorrect_file_type)

    def test_CreateDataFile_WhenCalledWithCorrectParameters_ReturnsCreatedDataFile(self):
        correct_file_data = TemporaryUploadedFile(content_type = 'text/text', size = 0, charset = 'UTF-8', name = 'file.txt')
        correct_device = self.mockDevice
        correct_start_date = datetime.datetime(2016, 2, 2, 1, 0, 0, 0, tzinfo=pytz.UTC)
        correct_file_type = 'S'

        data_file = self.data_file_service.create_data_file(correct_file_data, correct_device, correct_start_date, correct_file_type)

        self.assertIsInstance(data_file, DataFile)
        self.assertEqual(data_file.file_type, correct_file_type)
        self.assertEqual(data_file.device, correct_device)
        self.assertIsNotNone(data_file.file_uri)

    def test_CreateDataFile_WhenCalledWithCorrectParameters_CallsFileStorageService_SaveFile(self):
        correct_file_data = TemporaryUploadedFile(content_type = 'text/text', size = 0, charset = 'UTF-8', name = 'file.txt')
        correct_device = self.mockDevice
        correct_start_date = datetime.datetime(2016, 2, 2, 1, 0, 0, 0, tzinfo=pytz.UTC)
        correct_file_type = 'S'

        data_file = self.data_file_service.create_data_file(correct_file_data, correct_device, correct_start_date, correct_file_type)

        self.file_storage_service.save_form_file.assert_called_once()

from .services.profile_service import ProfileService
from .services.ml_service import MLService
from .services.google_drive_service import GoogleDriveService

import pandas as pd
import numpy as np

# ProfileService
class ProfileServiceTestCase(TestCase):
    def setUp(self):
        self.ml_service = MLService()
        self.file_storage_service = GoogleDriveService()

        self.profile_service = ProfileService(self.ml_service, self.file_storage_service)

    def test_Authorize_WhenCalled_ReturnsMLPredictionResult(self):
        data_portion_df = pd.DataFrame()
        self.ml_service.create_dataframe_from_jsondata = MagicMock(return_value = data_portion_df)
        aggregated_data_portion_df = pd.DataFrame()
        self.ml_service.aggregate_data_portion_with_stats_functions = MagicMock(return_value = aggregated_data_portion_df)
        device = Device(id = '1', token = '1234')

        self.ml_service.predict = MagicMock(return_value = 0.7)
        received_auth_result = self.profile_service.authorize(device, '["one_sensor_data_portion"]')

        self.assertEqual(received_auth_result, 0.7)

from .services.simple_auth_service import SimpleAuthService

# SimpleAuthService
class SimpleAuthServiceTestCase(TestCase):
    def setUp(self):
        self.auth_service = SimpleAuthService()

        self.mockDevice1 = Device(id = '1', token = '1234')
        self.mockDevice2 = Device(id = '2', token = '2345')

        self.mockDevice1.save()
        self.mockDevice2.save()

    # verify_device_token
    def test_VerifyDeviceToken_WhenCalledWithCorrectToken_ReturnsTrue(self):
        token = '1234'

        result = self.auth_service.verify_device_token(self.mockDevice1, token)

        self.assertTrue(result)

    def test_VerifyDeviceToken_WhenCalledWithIncorrectToken_ReturnsFalse(self):
        token = '2345'

        result = self.auth_service.verify_device_token(self.mockDevice1, token)

        self.assertFalse(result)