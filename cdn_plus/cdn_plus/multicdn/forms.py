# myapp/forms.py

from django import forms

class CdnForm(forms.Form):
    aws_access_key = forms.CharField(label='Password', widget=forms.PasswordInput)
    aws_secret_access_key = forms.CharField(label='Password', widget=forms.PasswordInput)
    aws_region = forms.CharField(label='Password', widget=forms.PasswordInput)


