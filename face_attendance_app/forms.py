from django import forms
from profiles.models import Profile, Log
from django.contrib.auth.models import User
import base64
from django.core.files.base import ContentFile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        
        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError('Passwords do not match')
        
        return password_confirmation
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo','bio']
        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs['rows'] = 5
        self.fields['photo'] = forms.CharField(widget=forms.HiddenInput())
    

