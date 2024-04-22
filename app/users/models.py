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


class AppErrorReport(models.Model):
    user = models.ForeignKey(to=CustomUser, blank=True, null=True, on_delete=models.SET_NULL)
    msg = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.created} - {self.msg}"

