
from django.db import models
from django.conf import settings
from django.utils import timezone

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # вместо User
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['-created_at']

    def __str__(self):
        return f'Профиль {self.user.username}'

    @property
    def is_active(self):
        return self.user.is_active

    
 