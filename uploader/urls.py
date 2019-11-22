from django.urls import path, re_path

from . import views

app_name = 'uploader'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:data_file_id>/', views.details, name='details'),
    path('add/', views.add, name='add'),
]