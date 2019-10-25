from django.urls import path, re_path

from . import views

app_name = 'uploader'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:df_id>/', views.details, name='details'),
    path('add/', views.add, name='add'),
    # re_path(r'(?P<device_id>\d+)/(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/', views.find, name='find'),
]