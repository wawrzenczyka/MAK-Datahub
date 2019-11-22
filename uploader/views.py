import csv
import uuid
import logging

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import UploadFileForm

from core.services.simple_auth_service import SimpleAuthService
from core.services.device_service import DeviceService
from core.services.data_file_service import DataFileService
from core.services.google_drive_service import GoogleDriveService

from core.utils import get_form_error_message

logger = logging.getLogger(__name__)

def index(request):
    if request.method != 'GET':
        return HttpResponse('Invalid method')

    file_list = DataFileService.get_data_file_list()
    
    context = {
        'file_list': file_list,
    }
    return render(request, 'uploader/index.html', context)

def details(request, data_file_id):
    if request.method != 'GET':
        return HttpResponse('Invalid method')

    data_file = DataFileService.get_data_file(data_file_id)
    if data_file == None:
        return HttpResponse('File not found')

    content = GoogleDriveService.get_file(data_file.file_uri)
    
    response = HttpResponse(content, content_type="application/octet-stream")
    response['Content-Disposition'] = f'attachment; filename="{str(data_file)}.bin"'

    return response

@csrf_exempt
def add(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            sensor_file_data, event_file_data = request.FILES['sensor_file'], request.FILES['event_file']
            app_token, device_token, device_id, start_date = \
                request.POST['app_token'], request.POST['device_token'], request.POST['device_id'], request.POST['start_date']

            logger.info(f'Upload request received for device ${device_id}\n\tdevice_token: ${device_token}\n\tapp_token: ${app_token}\n\tstart_date: ${start_date}')

            if not SimpleAuthService.verify_app_token(app_token):
                logger.error(f'Upload request DENIED for device ${device_id} - application token ${app_token} is not valid')
                return JsonResponse({ 'error': f'Invalid application token ${app_token}' })

            device = DeviceService.get_device(device_id)

            if device != None:
                if not SimpleAuthService.verify_device_token(device, device_token):
                    logger.error(f'Upload request DENIED for device ${device_id} - device token ${device_token} is not valid')
                    return JsonResponse({ 'error': f'Invalid device token ${device_token}' })
                    
                logger.info(f'Upload request for device ${device_id} - device ${device_id} present in the database')
            else:
                device = DeviceService.create_device(device_id)
                logger.info(f'Upload request for device ${device_id} - device created, assigned token ${device.token}')

            sensor_data_file = DataFileService.create_data_file(sensor_file_data, device, start_date, 'S')
            logger.info(f'Upload request for device ${device_id} - sensor file uploaded')
            event_data_file = DataFileService.create_data_file(event_file_data, device, start_date, 'E')
            logger.info(f'Upload request for device ${device_id} - event file uploaded')

            return JsonResponse({ 'device_token': device.token, 'sensor_file': sensor_file_data.name, 'event_file': event_file_data.name })
        else:
            error = get_form_error_message(form)
            logger.error(f'Upload request DENIED for device ${device_id} - ' + error)
            return JsonResponse({ 'error': error })
    logger.error(f'Received non-POST upload request')
    return JsonResponse({ 'error': 'Upload should be POST' })

