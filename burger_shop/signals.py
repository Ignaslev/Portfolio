from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    '''
    Automatically creates a Profile instance when a new User is registered.

    Triggered by the post_save signal of the User model.
    '''
    if created:
        Profile.objects.create(user=instance)
