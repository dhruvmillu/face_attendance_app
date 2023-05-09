from django.contrib.auth.models import User
from profiles.models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Log

@receiver(post_save, sender=Profile) # When a user is saved, send this signal
def create_profile(sender, instance, created, **kwargs): # When a user is saved, send this signal
    if created: # If a user is created
        Log.objects.create(user=instance) # Create a profile for the user