from django.conf import settings
from django.contrib.sites.models import Site
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from twilio.rest import TwilioRestClient


def get_full_url(url):
    return Site.objects.get_current().domain + url


def make_call(call_entry):
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    param = Signer().sign(call_entry.pk)
    url = get_full_url(reverse('caller:callback_call', args=(param,)))
    manager_phone = call_entry.manager_phone
    if manager_phone is None:
        call_entry.fail()
        return
    client.calls.create(manager_phone.number, settings.TWILIO_DEFAULT_FROM, url,
                        status_callback=get_full_url(reverse('caller:callback_result', args=(param,))),
                        status_method='GET', method='GET', timeout=5, record=True)


def make_stub_success_call(call_entry):
    call_entry.success()


def make_stub_failed_call(call_entry):
    call_entry.fail()


def make_stub_call(call_entry):
    pass
