from django.conf import settings
from django.core.signing import Signer, BadSignature
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from twilio.twiml import Response

from callback_request.models import CallEntry


def get_call_entry(**kwargs):
    try:
        pk = Signer().unsign(kwargs['id'])
    except BadSignature:
        raise Http404
    return get_object_or_404(CallEntry, pk=pk)


class CallbackCall(View):
    def dispatch(self, request, *args, **kwargs):
        print(request.GET)
        call_entry = get_call_entry(**kwargs)
        resp = Response()
        resp.say('Соединяю с клиентом, оставайтесь на линии', voice='alice', language='ru-RU')
        dial = resp.dial(callerId=settings.TWILIO_DEFAULT_FROM)
        dial.number(call_entry.request.phone)
        return HttpResponse(str(resp), content_type='text/xml')


class CallbackCallResult(View):
    def dispatch(self, request, *args, **kwargs):
        print(request.GET)
        call_entry = get_call_entry(**kwargs)
        call_status = request.GET['CallStatus']
        if call_status == 'in-progress':
            call_entry.state = 'in-progress'
            call_entry.save()
        elif call_status == 'completed':
            call_entry.record_url = request.GET.get('RecordingUrl', None)
            call_entry.duration = request.GET.get('RecordingDuration', 0)
            call_entry.success()
        elif call_status == 'no-answer':
            call_entry.fail()
        else:
            raise Exception('Unknown state: ' + call_status)
        return HttpResponse('ok')
