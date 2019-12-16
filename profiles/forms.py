import json

from django import forms

class GetProfileForm(forms.Form):
    device_id = forms.CharField(max_length=50)
    app_token = forms.CharField(max_length=36)
    device_token = forms.CharField(max_length=36)

class GetAuthResultForm(forms.Form):
    device_id = forms.CharField(max_length=50)
    app_token = forms.CharField(max_length=36)
    device_token = forms.CharField(max_length=36)
    sensor_data = forms.CharField()
    
    def clean_sensor_data(self):
        json_string = self.cleaned_data['sensor_data']
        try:
            json_data = json.loads(json_string)
            if type(json_data) is not list:
                raise forms.ValidationError("Invalid json structure")
            for json_row in json_data:
                if len(json_row) != 6*4 + 1:
                    raise forms.ValidationError("Json should have 19 columns")
                if type(json_row) is not list:
                    raise forms.ValidationError("Invalid json structure")
                for value in json_row:
                    if type(value) is not float and type(value) is not int:
                        raise forms.ValidationError("Invalid json structure")
        except:
            raise forms.ValidationError("Invalid data in sensor_data")
        return json_string