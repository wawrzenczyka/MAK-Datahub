from django.urls import path

from . import views

app_name = 'profiles'
urlpatterns = [
    path('get/', views.get_profile, name='get'),
]