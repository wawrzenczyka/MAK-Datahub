import csv
import uuid
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(levelname)s - %(message)s')

import services.google_drive_service as drive

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from .models import DataFile, Device
from .forms import UploadFileForm

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def index(request):
    file_list = DataFile.objects.order_by('device_id', '-start_date')
    
    context = {
        'file_list': file_list,
    }
    return render(request, 'uploader/index.html', context)

def details(request, df_id):
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

            logging.error(f'Device id: ${device_id}, upload request\n\tdevice_token: ${device_token}\n\tapp_token: ${app_token}\n\tstart_date: ${start_date}')

            if app_token != '944d5555-48bf-48b2-b690-0065b9ba0bdd':
                logging.error(f'Device id: ${device_id}, start date: ${start_date} - Invalid application token ${app_token}')
                return JsonResponse({ 'error': 'Invalid application token, access denied' })

            try:
                dev = Device.objects.get(id = device_id)
                logging.error(f'Device id: ${device_id}, start_date: ${start_date} - Device already exists')
                if device_token != dev.token:
                    logging.error(f'Device id: ${device_id}, start_date: ${start_date} - Invalid device token ${device_token}')
                    return JsonResponse({ 'error': 'Invalid device token, access denied' })
            except Device.DoesNotExist:
                logging.error(f'Device id: ${device_id}, start_date: ${start_date} - Device created, generating token')
                device_token = uuid.uuid4()
                dev = Device(id = device_id, token = device_token)
                dev.save()

            df = DataFile(device = dev, start_date = start_date)
            
            filename = f'{device_id}_{file_data.name}'
            file_uri = drive.save_file(sensor_file_data, filename)
            df.file_uri = file_uri
            df.save()
            logging.error(f'Device id: ${device_id}, start_date: ${start_date} - Data file uploaded, returning device token ${device_token}')

            return JsonResponse({ 'device_token': str(device_token) })
        logging.error(f'Invalid form, parsing error')
        return JsonResponse({ 'error': 'Invalid form' })
    logging.error(f'Non-POST request received')
    return JsonResponse({ 'error': 'Upload should be POST' })
