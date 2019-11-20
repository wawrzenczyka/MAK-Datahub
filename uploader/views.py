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

            logger.debug(f'Device id: ${device_id}, upload request\n\tdevice_token: ${device_token}\n\tapp_token: ${app_token}\n\tstart_date: ${start_date}')

            if app_token != app_access_token:
                logger.error(f'Device id: ${device_id}, start date: ${start_date} - Invalid application token ${app_token}')
                return JsonResponse({ 'error': f'Invalid application token ${app_token}, access denied' })

            try:
                dev = Device.objects.get(id = device_id)
                logger.debug(f'Device id: ${device_id}, start_date: ${start_date} - Device already exists')
                if device_token != dev.token:
                    logger.error(f'Device id: ${device_id}, start_date: ${start_date} - Invalid device token ${device_token}')
                    return JsonResponse({ 'error': f'Invalid device token ${device_token}, access denied' })
            except Device.DoesNotExist:
                logger.debug(f'Device id: ${device_id}, start_date: ${start_date} - Device created, generating token')
                device_token = uuid.uuid4()
                dev = Device(id = device_id, token = device_token)
                dev.save()

            sensor_df = DataFile(device = dev, start_date = start_date, file_type = 'S')            
            sensor_filename = f'{device_id}_{sensor_file_data.name}'
            file_uri = drive.save_file(sensor_file_data, device_id, sensor_filename)
            sensor_df.file_uri = file_uri
            sensor_df.save()
            
            event_df = DataFile(device = dev, start_date = start_date, file_type = 'E')            
            event_filename = f'{device_id}_{event_file_data.name}'
            file_uri = drive.save_file(event_file_data, device_id, event_filename)
            event_df.file_uri = file_uri
            event_df.save()
            
            logger.debug(f'Device id: ${device_id}, start_date: ${start_date} - Data files uploaded, returning device token ${device_token}')

            return JsonResponse({ 'device_token': str(device_token), 'sensor_file': sensor_file_data.name, 'event_file': event_file_data.name })
        else:
            form_errors = 'Invalid form\n\t'
            for field in form.errors:
                form_errors += f'Field ${field} error: ${form.errors[field]}\n\t'
            logger.error(form_errors)
            return JsonResponse({ 'error': form_errors })
    logger.error(f'Non-POST request received')
    return JsonResponse({ 'error': 'Upload should be POST' })
