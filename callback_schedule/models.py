from django.conf import settings
from django.db import models
from django.utils.timezone import now


class CallbackManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    priority = models.IntegerField(default=0)

    @staticmethod
    def get_available_manager(when=None):
        if when is None:
            when = now()
        weekday = when.weekday()
        schedules = CallbackManagerSchedule.objects.filter(
            weekday=weekday, available_from__lte=when.time(), available_till__gte=when.time()
        ).order_by('-manager__priority')
        if schedules.exists():
            return schedules[0].manager
        return None


class CallbackManagerPhone(models.Model):
    manager = models.ForeignKey(CallbackManager)
    phone_type = models.CharField(max_length=32)
    number = models.CharField(max_length=255)


class CallbackManagerSchedule(models.Model):
    manager = models.ForeignKey(CallbackManager, related_name='schedule')
    weekday = models.IntegerField()
    available_from = models.TimeField()
    available_till = models.TimeField()
