import logging

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import GetProfileForm, GetAuthResultForm

from core.services.simple_auth_service import SimpleAuthService
from core.services.device_service import DeviceService
from core.services.profile_service import ProfileService
from core.services.google_drive_service import GoogleDriveService
from core.services.ml_service import MLService
from core.services.data_extraction_service import DataExtractionService

from core.utils import get_form_error_message

__logger = logging.getLogger(__name__)
__auth_service = SimpleAuthService()
__device_service = DeviceService()
__profile_service = ProfileService(MLService(), GoogleDriveService(), DataExtractionService())

@csrf_exempt
def get_profile(request):
    if request.method == 'GET':
        form = GetProfileForm(request.GET, request.FILES)
        if form.is_valid():
            app_token = form.cleaned_data['app_token']
            device_token = form.cleaned_data['device_token']
            device_id = form.cleaned_data['device_id']
            profile_type = form.cleaned_data['profile_type']

            __logger.info(f'Get profile request for device ${device_id} received\n\tapp_token: ${app_token}\n\tdevice_token: ${device_token}')

            if not __auth_service.verify_app_token(app_token):
                __logger.error(f'Get profile request DENIED for device ${device_id} - application token ${app_token} is not valid')
                return JsonResponse({ 'error': f'Invalid application token ${app_token}' })

            device = __device_service.get_device(device_id)
            if device != None:
                if not __auth_service.verify_device_token(device, device_token):
                    __logger.error(f'Get profile request DENIED for device ${device_id} - device token ${device_token} is not valid')
                    return JsonResponse({ 'error': f'Invalid device token ${device_token}' })
            else:
                __logger.error(f'Get profile request DENIED for device ${device_id} - device not registered')
                return JsonResponse({ 'error': f'Device ${device_id} is not registered' })
            
            profile_info, profile = __profile_service.get_latest_profile_for_device(device, profile_type)
            if (profile_info != None):
                __logger.info(f'Get profile request for device ${device_id} - profile ready, created: ${profile_info.run.run_date}')
                serialized_profile, serialized_support = __profile_service.serialize_profile(profile)
                return JsonResponse({ 'profile_ready': True, 'profile': serialized_profile, 'support': serialized_support, 'creation_date': profile_info.run.run_date })
            else:
                __logger.info(f'Get profile request for device ${device_id} - profile not ready')
                return JsonResponse({ 'profile_ready': False })
        else:
            device_id_string = f'(device id not submitted) '
            if 'device_id' in request.POST:
                device_id_string = f'(device ${str(request.POST["device_id"])}) '
            error = get_form_error_message(form)
            __logger.error(f'Get profile request DENIED {device_id_string}- ' + error)
            return JsonResponse({ 'error': error })
    __logger.error(f'Received non-GET get profile request')
    return JsonResponse({ 'error': 'Get profile request should be GET' })

@csrf_exempt
def get_auth_result(request):
    if request.method == 'POST':
        form = GetAuthResultForm(request.POST, request.FILES)

        if form.is_valid():
            app_token = form.cleaned_data['app_token']
            device_token = form.cleaned_data['device_token']
            device_id = form.cleaned_data['device_id']
            sensor_data = form.cleaned_data['sensor_data']
            profile_type = form.cleaned_data['profile_type']

            __logger.info(f'Get auth result request for device ${device_id} received\n\tapp_token: ${app_token}\n\tdevice_token: ${device_token}')

            if not __auth_service.verify_app_token(app_token):
                __logger.error(f'Get auth result request DENIED for device ${device_id} - application token ${app_token} is not valid')
                return JsonResponse({ 'error': f'Invalid application token ${app_token}' })

            device = __device_service.get_device(device_id)
            if device != None:
                if not __auth_service.verify_device_token(device, device_token):
                    __logger.error(f'Get auth result request DENIED for device ${device_id} - device token ${device_token} is not valid')
                    return JsonResponse({ 'error': f'Invalid device token ${device_token}' })
            else:
                __logger.error(f'Get auth result request DENIED for device ${device_id} - device not registered')
                return JsonResponse({ 'error': f'Device ${device_id} is not registered' })
            
            yes_proba = __profile_service.authorize(device, profile_type, sensor_data)
            if (yes_proba != None):
                __logger.info(f'Get auth result request for device ${device_id} - profile ready, probability of matching user: ${yes_proba * 100}%')
                return JsonResponse({ 'profile_ready': True, 'matching_user_probability': yes_proba })
            else:
                __logger.info(f'Get auth result request for device ${device_id} - profile not ready')
                return JsonResponse({ 'profile_ready': False })
        else:
            device_id_string = f'(device id not submitted) '
            if 'device_id' in request.POST:
                device_id_string = f'(device ${str(request.POST["device_id"])}) '
            error = get_form_error_message(form)
            __logger.error(f'Get auth result request DENIED {device_id_string}- ' + error)
            return JsonResponse({ 'error': error })
    __logger.error(f'Received non-POST get auth result request')
    return JsonResponse({ 'error': 'Get auth result request should be POST' })