from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt

from .models import DataFile
from .forms import UploadFileForm

def index(request):
    file_list = DataFile.objects.order_by('-start_date', '-device_id')
    
    context = {
        'file_list': file_list,
    }
    return render(request, 'uploader/index.html', context)

def details(request, df_id):
    df = get_object_or_404(DataFile, pk=df_id)
    return render(request, 'uploader/details.html', {'data_file': df})

@csrf_exempt
def add(request):    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_data = request.FILES['file']

            fs = FileSystemStorage()
            filename = fs.save(file_data.name, file_data)
            file_uri = fs.url(filename)

            df = DataFile(file_uri = file_uri, device_id = request.POST['device_id'], \
                start_date = request.POST['start_date'], end_date = request.POST['end_date'])
            df.save()

            return HttpResponse(file_uri)
        return HttpResponse('Invalid form')
    return HttpResponse('Upload should be POST')