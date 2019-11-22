import logging

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import GetProfileForm

from core.services.simple_auth_service import SimpleAuthService
from core.services.device_service import DeviceService
from core.services.profile_service import ProfileService

from core.utils import get_form_error_message

logger = logging.getLogger(__name__)

@csrf_exempt
def get_profile(request):        
    if request.method == 'GET':
        form = GetProfileForm(request.GET, request.FILES)
        if form.is_valid():
            app_token = request.GET['app_token']
            device_token = request.GET['device_token']
            device_id = request.GET['device_id']

            if not SimpleAuthService.verify_app_token(app_token):
                return JsonResponse({ 'error': f'Invalid application token ${app_token}, access denied' })

            device = DeviceService.get_device(device_id)
            if device != None:
                if not SimpleAuthService.verify_device_token(device, device_token):
                    return JsonResponse({ 'error': f'Invalid device token ${device_token}, access denied' })
            else:
                return JsonResponse({ 'error': f'Device ${device_id} is not registered' })
            
            profile_model, profile = ProfileService.get_profile_model_and_file(device)
            if (profile_model != None):
                return JsonResponse({ 'profile_ready': True, 'profile': profile, 'creation_date': profile_model.creation_date })
            else:
                return JsonResponse({ 'profile_ready': False })
        else:
            error = get_form_error_message(form)
            logger.error(error)
            return JsonResponse({ 'error': error })
    return JsonResponse({ 'error': 'Get profile request should be GET' })
