from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(
        "username",
        max_length=150,
        blank=True,
        null=True,
    )

    email = models.EmailField("email address", unique=True)

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)

    def str(self):
        return self.email or self.username
