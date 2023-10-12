from django.db import models
from django.contrib.auth.models import AbstractUser
from authentication.managers import SupportEngineerManager


# Create your models here.
class SupportEngineer(AbstractUser):
    objects = SupportEngineerManager()

    class Meta:
        db_table = "team_members"
        ordering = ["last_name", "first_name"]
        verbose_name = "Support Engineer"
        verbose_name_plural = "Support Engineers"

    def __str__(self):
        return self.first_name
