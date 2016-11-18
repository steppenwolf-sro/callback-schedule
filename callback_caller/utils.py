from django.conf import settings
from django.contrib.sites.models import Site
from twilio.rest import TwilioRestClient


def get_full_url(url):
    return settings.SCHEME + '://' + Site.objects.get_current().domain + url


def make_call(call_request):
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    url = get_full_url(call_request.get_absolute_url())
    client_phone = call_request.right_phone

    # TODO: Add status callback
    client.calls.create(client_phone, settings.TWILIO_DEFAULT_FROM, url,
                        status_method='GET', status_callback='',
                        method='GET', timeout=settings.CALLBACK_CLIENT_CALL_TIMEOUT)


def make_stub_success_call(call_request):
    call_request.get_entry().success()


def make_stub_failed_call(call_request):
    call_request.get_entry().fail()


def make_stub_call(call_entry):
    pass
