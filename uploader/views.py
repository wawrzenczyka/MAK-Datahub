import csv
import uuid
import services.google_drive_service as drive

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, StreamingHttpResponse
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
    file_list = DataFile.objects.order_by('-start_date', '-device_id')
    
    context = {
        'file_list': file_list,
    }
    return render(request, 'uploader/index.html', context)

def details(request, df_id):
    df = get_object_or_404(DataFile, pk=df_id)

    content = drive.get_file(df.file_uri)
    
    response = HttpResponse(content, content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{str(df)}.csv"'

    return response

@csrf_exempt
def add(request):    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_data = request.FILES['file']
            token = request.POST['token']

            try:
                dev = Device.objects.get(id = request.POST['device_id'])
                if token != dev.token:
                    return HttpResponse('Invalid token')
            except ObjectDoesNotExist:
                token = uuid.uuid4()
                dev = Device(id = request.POST['device_id'], token = token)
                dev.save()

            file_uri = drive.save_file(file_data)

            df = DataFile(file_uri = file_uri, device = dev, \
                start_date = request.POST['start_date'], end_date = request.POST['end_date'])
            df.save()

            return HttpResponse(file_uri + ' ' + str(token))
        return HttpResponse('Invalid form')
    return HttpResponse('Upload should be POST')
