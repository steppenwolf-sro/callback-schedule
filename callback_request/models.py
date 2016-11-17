import re
from uuid import uuid1

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.module_loading import import_string

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
    phones = models.ManyToManyField(CallbackManagerPhone, blank=True)

    @property
    def right_phone(self):
        return '+' + re.sub('[^0-9]', '', self.phone)

    def get_phone_at(self, attempt):
        try:
            return self.phones.all().order_by('priority')[attempt]
        except IndexError:
            return None


class CallEntry(models.Model):
    STATES = (
        ('processing', 'Processing'),
        ('in-progress', 'In Progress'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    created = models.DateTimeField(auto_now_add=True)
    request = models.ForeignKey(CallbackRequest)
    attempt = models.IntegerField(default=0)
    state = models.CharField(max_length=32, choices=STATES, default='processing')
    record_url = models.URLField(blank=True, null=True)
    duration = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid1)

    @property
    def manager_phone(self):
        return self.request.get_phone_at(self.attempt)

    def fail(self):
        self.state = 'failed'
        self.save()
        if self.request.phones.all().count() > self.attempt + 1:
            CallEntry.objects.create(request=self.request, attempt=self.attempt + 1)

    def success(self):
        self.state = 'success'
        self.save()

    def make_call(self):
        caller = import_string(settings.CALLER_FUNCTION)
        caller(self)


@receiver(post_save, sender=CallbackRequest, dispatch_uid='create_call_entry_on_request')
def create_callback_entry(sender, instance, created, **kwargs):
    if created and instance.immediate:
        for phone in CallbackManagerPhone.get_available_phones():
            instance.phones.add(phone)
        CallEntry.objects.create(request=instance)


@receiver(post_save, sender=CallEntry, dispatch_uid='make_call_on_call_entry')
def make_calls(sender, instance, created, **kwargs):
    if created:
        instance.make_call()
