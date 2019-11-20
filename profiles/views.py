import logging

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from uploader.models import Device
from .models import ProfileFile
from .forms import GetProfileForm
from application_access_token import app_access_token

logger = logging.getLogger(__name__)

@csrf_exempt
def get_profile(request):        
    if request.method == 'GET':
        form = GetProfileForm(request.GET, request.FILES)
        if form.is_valid():
            app_token = request.GET['app_token']
            device_token = request.GET['device_token']
            device_id = request.GET['device_id']

            if app_token != app_access_token:
                logger.error(f'Device id: ${device_id} getting profile - Invalid application token ${app_token}')
                return JsonResponse({ 'error': f'Invalid application token ${app_token}, access denied' })

            try:
                dev = Device.objects.get(id = device_id)
                logger.debug(f'Device id: ${device_id} getting profile - Success')
                if device_token != dev.token:
                    logger.error(f'Device id: ${device_id} getting profile - Invalid device token ${device_token}')
                    return JsonResponse({ 'error': f'Invalid device token ${device_token}, access denied' })
                else:
                    try:
                        profile_filename = dev.profilefile
                        return JsonResponse({ 'profile': [0, 0, 0, 0] })
                    except ProfileFile.DoesNotExist:
                        return JsonResponse({ 'error': 'Profile is not yet ready' })
            except Device.DoesNotExist:
                logger.error(f'Device id: ${device_id} getting profile - Device is not registered')
                return JsonResponse({ 'error': 'Device is not registered' })

        else:
            form_errors = 'Invalid form\n\t'
            for field in form.errors:
                form_errors += f'Field ${field} error: ${form.errors[field]}\n\t'
            logger.error(form_errors)
            return JsonResponse({ 'error': form_errors })
    return JsonResponse({ 'error': 'Upload should be GET' })

