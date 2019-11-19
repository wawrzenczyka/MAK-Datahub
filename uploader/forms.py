from django import forms

class UploadFileForm(forms.Form):
    sensor_file = forms.FileField()
    event_file = forms.FileField()
    device_id = forms.CharField(max_length=50)
    app_token = forms.CharField(max_length=36)
    device_token = forms.CharField(max_length=36)
    start_date = forms.DateTimeField()