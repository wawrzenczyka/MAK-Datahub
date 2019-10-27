from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    device_id = forms.CharField(max_length=50)
    token = forms.CharField(max_length=36)
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()