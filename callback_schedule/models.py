from django.conf import settings
from django.db import models


class CallbackManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    priority = models.IntegerField(default=0)

    @staticmethod
    def get_available_manager(when=None):
        raise NotImplementedError


class CallbackManagerPhone(models.Model):
    manager = models.ForeignKey(CallbackManager)
    phone_type = models.CharField(max_length=32)
    number = models.CharField(max_length=255)


class CallbackManagerSchedule(models.Model):
    manager = models.ForeignKey(CallbackManager, related_name='schedule')
    weekday = models.IntegerField()
    available_from = models.TimeField()
    available_till = models.TimeField()
