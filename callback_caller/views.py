from django.core.signing import Signer, BadSignature
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from twilio.twiml import Response

from callback_caller.utils import get_full_url
from callback_request.models import CallEntry, CallbackRequest


def get_call_request(model, **kwargs):
    try:
        pk = Signer().unsign(kwargs['id'])
    except BadSignature:
        raise Http404
    return get_object_or_404(model, pk=pk)


class CallbackCall(View):
    def dispatch(self, request, *args, **kwargs):
        print(request.GET)
        call_request = get_call_request(CallbackRequest, **kwargs)
        resp = Response()
        entry = call_request.get_entry()
        if entry is None:
            resp.say('Нет свободных менеджеров', voice='alice', language='ru-RU')
        else:
            resp.say('Соединяю с менеджером, оставайтесь на линии', voice='alice', language='ru-RU')
            dial = resp.dial(callerId=call_request.right_phone,
                             action=get_full_url(entry.get_absolute_url()),
                             method='GET', record=True, timeout=5)
            dial.number(entry.phone.number)
        return HttpResponse(str(resp), content_type='text/xml')


class CallEntryResult(View):
    def dispatch(self, request, *args, **kwargs):
        print(request.GET)
        entry = get_call_request(CallEntry, **kwargs)

        status = request.GET['DialCallStatus']

        resp = Response()
        if status == 'no-answer':
            entry.fail()
            next_entry = entry.request.get_entry()
            if next_entry is None:
                resp.say('Нет свободных менеджеров', voice='alice', language='ru-RU')
            else:
                dial = resp.dial(callerId=next_entry.request.right_phone,
                                 action=get_full_url(next_entry.get_absolute_url()),
                                 method='GET', record=True, timeout=5)
                dial.number(next_entry.phone.number)
        elif status == 'completed':
            entry.record_url = request.GET.get('RecordingUrl', None)
            entry.duration = request.GET.get('RecordingDuration', 0)
            entry.success()
            resp.hangup()
        else:
            raise Exception('Wrong status: %s' % status)
        return HttpResponse(str(resp), content_type='text/xml')
