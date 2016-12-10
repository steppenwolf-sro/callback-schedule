from django.conf import settings
from django.contrib.sites.models import Site

from callback_caller.clients import RestClientVoximplant


def get_full_url(url):
    return settings.SCHEME + '://' + Site.objects.get_current().domain + url


def make_call(call_request):
    client = RestClientVoximplant()
    url = get_full_url(call_request.get_absolute_url())
    client_phone = call_request.right_phone

    client.create_call(client_phone=client_phone, url=url,
                       status_callback=get_full_url(call_request.get_client_callback_url()))


def make_stub_success_call(call_request):
    call_request.get_entry().success()


def make_stub_failed_call(call_request):
    call_request.get_entry().fail()


def make_stub_call(call_entry):
    pass
