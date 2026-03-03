from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')

    first_name = models.CharField(max_length=25, verbose_name='Имя', blank=True, null=True)
    last_name = models.CharField(max_length=35, verbose_name='Фамилия', blank=True, null=True)

    token = models.CharField(max_length=100, verbose_name='Токен', blank=True, null=True)

    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email