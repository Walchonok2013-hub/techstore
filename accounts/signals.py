from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile = apps.get_model('accounts', 'Profile')
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    try:
        Profile = apps.get_model('accounts', 'Profile')
        profile = instance.profile
        profile.save()
    except Profile.DoesNotExist:
        pass

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.conf import settings
# from .models import Profile

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(sender, instance, **kwargs):
#     # Если профиль уже есть, просто сохраняем его (на случай изменений)
#     try:
#         instance.profile.save()
#     except Profile.DoesNotExist:
#         pass