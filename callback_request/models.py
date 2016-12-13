import re

from django.conf import settings
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.module_loading import import_string

from callback_request.tasks import delayed_request
from callback_schedule.models import CallbackManager, CallbackManagerPhone


class CallbackRequest(models.Model):
    ERRORS = (
        ('no-answer', 'Client did not answer'),
        ('wrong-number', 'Wrong phone number'),
        ('no-manager', 'No free manager'),
    )
    client = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='callback_requests')
    created = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(blank=True, null=True)
    immediate = models.BooleanField(default=False)
    error = models.CharField(max_length=32, blank=True, choices=ERRORS)

    def __str__(self):
        return '#{} [{}]'.format(self.pk, self.created)

    @property
    def right_phone(self):
        return '+' + re.sub('[^0-9]', '', self.phone)

    def make_call(self):
        if self.get_entry() is None:
            self.error = 'no-manager'
            self.save()
            return
        caller = import_string(settings.CALLER_FUNCTION)
        caller(self)

    def get_absolute_url(self):
        return reverse('callback_caller:callback_call', args=(Signer().sign(self.pk),))

    def get_entry(self):
        try:
            return self.callentry_set.filter(state='waiting')[0]
        except IndexError:
            return None

    def get_client_callback_url(self):
        return reverse('callback_caller:callback_client_callback', args=(Signer().sign(self.pk),))

    def client_not_answered(self):
        self.completed = True
        self.error = 'no-answer'
        self.save()
        self.callentry_set.all().update(state='canceled')

    def wrong_number(self):
        self.completed = True
        self.error = 'wrong-number'
        self.save()
        self.callentry_set.all().update(state='canceled')

    def process(self):
        for phones in CallbackManagerPhone.get_available_phones():
            entry = CallEntry.objects.create(request=self)
            entry.phones.add(*phones)
        self.make_call()


class CallEntry(models.Model):
    STATES = (
        ('waiting', 'Waiting'),
        ('direct', 'Direct'),
        ('canceled', 'Canceled'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('no-answer', 'No answer'),
    )
    created = models.DateTimeField(auto_now_add=True)
    request = models.ForeignKey(CallbackRequest)
    state = models.CharField(max_length=32, choices=STATES, default='waiting')
    record_url = models.URLField(blank=True, null=True)
    duration = models.IntegerField(default=0)
    phone = models.ForeignKey(CallbackManagerPhone, blank=True, null=True, related_name='used_phones')
    manager = models.ForeignKey(CallbackManager, blank=True, null=True)
    phones = models.ManyToManyField(CallbackManagerPhone, related_name='phones')

    def get_absolute_url(self):
        return reverse('callback_caller:callback_result', args=(Signer().sign(self.pk),))

    def fail(self):
        self.state = 'failed'
        self.save()

    def success(self):
        self.state = 'success'
        self.save()
        self.request.completed = True
        self.request.save()
        CallEntry.objects.filter(request=self.request, pk__gt=self.pk).update(state='canceled')


@receiver(post_save, sender=CallbackRequest, dispatch_uid='create_call_entry_on_request')
def create_callback_entry(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.immediate:
        instance.process()
    elif settings.CALLBACK_PROCESS_DELAYED:
        delayed_request.apply_async((instance.pk,), eta=instance.date)
