import csv
import uuid
import logging

import services.google_drive_service as drive

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from .models import DataFile, Device
from .forms import UploadFileForm
from application_access_token import app_access_token

from services.simple_auth_service import SimpleAuthService
from services.device_service import DeviceService
from services.data_file_service import DataFileService

logger = logging.getLogger(__name__)

def index(request):
    if request.method != 'GET':
        return HttpResponse('Invalid method')
    
    file_list = DataFile.objects.order_by('device_id', '-start_date')
    
    context = {
        'file_list': file_list,
    }
    return render(request, 'uploader/index.html', context)

def details(request, df_id):
    if request.method != 'GET':
        return HttpResponse('Invalid method')

    df = get_object_or_404(DataFile, pk=df_id)

    content = drive.get_file(df.file_uri)
    
    response = HttpResponse(content, content_type="application/octet-stream")
    response['Content-Disposition'] = f'attachment; filename="{str(df)}.bin"'

    return response

@csrf_exempt
def add(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            sensor_file_data = request.FILES['sensor_file']
            event_file_data = request.FILES['event_file']

            app_token = request.POST['app_token']
            device_token = request.POST['device_token']
            device_id = request.POST['device_id']
            start_date = request.POST['start_date']

            logger.info(f'Device id: ${device_id}, upload request\n\tdevice_token: ${device_token}\n\tapp_token: ${app_token}\n\tstart_date: ${start_date}')

            if not SimpleAuthService.verify_app_token(app_token):
                return JsonResponse({ 'error': f'Invalid application token ${app_token}, access denied' })

            device = DeviceService.get_device(device_id)

            if device != None:
                if not SimpleAuthService.verify_device_token(device, device_token):
                    return JsonResponse({ 'error': f'Invalid device token ${device_token}, access denied' })
                    
                logger.info(f'Device ${device_id} present in the database')
            else:
                device = DeviceService.create_device(device_id)
                logger.info(f'Device ${device_id} created, assigned token ${device.token}')

            sensor_data_file = DataFileService.create_data_file(sensor_file_data, device, start_date, 'S')
            event_data_file = DataFileService.create_data_file(event_file_data, device, start_date, 'E')
            
            logger.info(f'Device id: ${device_id}, start_date: ${start_date} - Data files uploaded, returning device token ${device_token}')

            return JsonResponse({ 'device_token': str(device_token), 'sensor_file': sensor_file_data.name, 'event_file': event_file_data.name })
        else:
            form_errors = 'Invalid form\n\t'
            for field in form.errors:
                form_errors += f'Field ${field} error: ${form.errors[field]}\n\t'
            logger.error(form_errors)
            return JsonResponse({ 'error': form_errors })
    logger.error(f'Non-POST request received')
    return JsonResponse({ 'error': 'Upload should be POST' })
