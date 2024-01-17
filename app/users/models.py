from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)

    def str(self):
        return self.email or self.username
