import os
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(pre_save, sender=Profile)
def delete_old_profile_picture(sender, instance, **kwargs):
    """Delete old profile picture when a new one is uploded"""
    if not instance.pk:
        return

    try:
        old_picture = Profile.objects.get(pk=instance.pk).profile_picture
    except:
        return

    new_picture = instance.profile_picture
    if old_picture and old_picture != new_picture and os.path.isfile(old_picture.path):
        os.remove(old_picture.path)

@receiver(post_delete, sender=Profile)
def delete_profile_pic_on_delete(sender, instance, **kwargs):
    """"Delete file when Profile is deleted."""
    if instance.profile_picture and os.path.isfile(instance.profile_picture.path):
        os.remove(instance.profile_picture.path)
