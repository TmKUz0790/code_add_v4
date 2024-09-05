from django.db import models
from django.contrib.auth.models import User

class UserChoice(models.Model):
    choice = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.choice} - {self.serial_number}"
