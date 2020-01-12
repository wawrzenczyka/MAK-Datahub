import dependency_injector.containers as containers
import dependency_injector.providers as providers

from ProfileCreator.parsers.event_parser import EventParser
from ProfileCreator.parsers.sensors_parser import SensorParser

class Parsers(containers.DeclarativeContainer):
    """IoC container of parser providers."""
    event_parser = providers.Factory(EventParser)
    sensor_parser = providers.Factory(SensorParser, config_json_path = 'ProfileCreator/parsers/sensor_config.json')

from core.services.data_extraction_service import DataExtractionService
from core.services.data_file_service import DataFileService
from core.services.device_service import DeviceService
from core.services.storage_service import GoogleDriveService
from core.services.ml_service import RFE10_RF100_SMOTE_MLService
from core.services.profile_service import ProfileService
from core.services.simple_auth_service import SimpleAuthService

class Services(containers.DeclarativeContainer):
    """IoC container of service providers."""
    auth_service = providers.Factory(SimpleAuthService)
    device_service = providers.Factory(DeviceService)
    ml_service = providers.Factory(RFE10_RF100_SMOTE_MLService)
    storage_service = providers.Factory(GoogleDriveService)

    data_extraction_service = providers.Factory(DataExtractionService, event_parser = Parsers.event_parser, sensor_parser = Parsers.sensor_parser)
    data_file_service = providers.Factory(DataFileService, storage_service = storage_service)
    profile_service = providers.Factory(ProfileService, ml_service = ml_service, storage_service = storage_service, \
        data_extraction_service = data_extraction_service, device_service = device_service)