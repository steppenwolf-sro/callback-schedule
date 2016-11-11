import re

from django.conf import settings
from django.db import models


class CallbackRequest(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(blank=True, null=True)
    immediate = models.BooleanField(default=False)

    @property
    def right_phone(self):
        return '+' + re.sub('[^0-9]', '', self.phone)
