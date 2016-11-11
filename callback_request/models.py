import re
from uuid import uuid1

from django.conf import settings
from django.db import models

from callback_schedule.models import CallbackManager, CallbackManagerPhone


class CallbackRequest(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(blank=True, null=True)
    immediate = models.BooleanField(default=False)
    managers = models.ManyToManyField(CallbackManager)

    @property
    def right_phone(self):
        return '+' + re.sub('[^0-9]', '', self.phone)


class CallEntry(models.Model):
    manager = models.ForeignKey(CallbackManager)
    created = models.DateTimeField(auto_now_add=True)
    request = models.ForeignKey(CallbackRequest)
    manager_phone = models.ForeignKey(CallbackManagerPhone)
    succeeded = models.BooleanField(default=False)
    record_url = models.URLField(blank=True, null=True)
    duration = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid1)
