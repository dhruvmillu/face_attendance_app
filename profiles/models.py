from djongo import models
from datetime import datetime
# Create your models h
from django.contrib.auth.models import User




def user_directory_path(instance, filename):
  
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    return 'profile/user_{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    photo = models.ImageField(upload_to = user_directory_path)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, default='alpha')
    
    def __str__(self):
        return f'{self.user.username} Profile'

def user_directory_path_log(instance, filename):
    print(instance.profile.user.username)
    print(filename)
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    print('attendance/{0}'.format(filename))
    return 'attendance/{0}/{1}'.format(instance.profile.user.username,filename)

class Log(models.Model):
    profile = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path_log)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.profile.id} Log'