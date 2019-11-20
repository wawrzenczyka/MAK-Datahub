from django import forms

class GetProfileForm(forms.Form):
    device_id = forms.CharField(max_length=50)
    app_token = forms.CharField(max_length=36)
    device_token = forms.CharField(max_length=36)