from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class CallbackManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.user.username


class CallbackManagerPhone(models.Model):
    manager = models.ForeignKey(CallbackManager)
    phone_type = models.CharField(max_length=32)
    number = models.CharField(max_length=255)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return '[{}] {}'.format(self.phone_type, self.number)

    @staticmethod
    def get_available_phones(when=None):
        if when is None:
            when = now()
        weekday = when.weekday()
        schedules = CallbackManagerSchedule.objects.filter(
            weekday=weekday, available_from__lte=when.time(), available_till__gte=when.time()
        )
        priorities = CallbackManagerPhone.objects.filter(manager__schedule__in=schedules).distinct() \
            .order_by('priority').values_list('priority', flat=True)
        result = []
        for priority in priorities:
            result.append(CallbackManagerPhone.objects.filter(
                manager__schedule__in=schedules,
                priority=priority
            ).distinct())
        return result


class CallbackManagerScheduleQueryset(models.QuerySet):
    def for_date(self, date: 'datetime'):
        if date < now():
            return self.none()
        return self.filter(weekday=date.weekday(), available_from__lte=date.time(), available_till__gte=date.time())


class CallbackManagerSchedule(models.Model):
    manager = models.ForeignKey(CallbackManager, related_name='schedule')
    weekday = models.IntegerField()
    available_from = models.TimeField()
    available_till = models.TimeField()

    objects = CallbackManagerScheduleQueryset.as_manager()
