from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User) # When a user is saved, send this signal
def create_profile(sender, instance, created, **kwargs): # When a user is saved, send this signal
    if created: # If a user is created
        Profile.objects.create(user=instance) # Create a profile for the user