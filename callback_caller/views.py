from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.signing import Signer, BadSignature
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from twilio.twiml import Response
from twilio.util import TwilioCapability

from callback_caller.utils import get_full_url
from callback_request.models import CallEntry, CallbackRequest
from callback_schedule.models import CallbackManager


def get_call_request(model, **kwargs):
    try:
        pk = Signer().unsign(kwargs['id'])
    except BadSignature:
        raise Http404
    return get_object_or_404(model, pk=pk)


class CallbackCall(View):
    """
    View is called by Twilio, when client has answered the phone
    """

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
    """
    View is called by Twilio, when the call has ended.
    """

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
                                 method='GET', record=True, timeout=settings.CALLBACK_MANAGER_CALL_TIMEOUT)
                dial.number(next_entry.phone.number)
        elif status == 'completed':
            entry.record_url = request.GET.get('RecordingUrl', None)
            entry.duration = request.GET.get('RecordingDuration', 0)
            entry.success()
            resp.hangup()
        else:
            raise Exception('Wrong status: %s' % status)
        return HttpResponse(str(resp), content_type='text/xml')


class TokenRequest(View):
    """
    Registers JS client and returns token for logging into twilio JS API
    """

    def dispatch(self, request, *args, **kwargs):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        application_sid = settings.TWILIO_CALLBACK_APP_SID

        capability = TwilioCapability(account_sid, auth_token)
        capability.allow_client_outgoing(application_sid)
        token = capability.generate()

        manager = request.user.callbackmanager

        return JsonResponse({'token': token, 'manager': Signer().sign(manager.pk)})


class DirectCallRequest(View):
    """
    View is called by Twilio, when manager has made direct call.
    Manager client app MUST provide params:
        - manager: manager token, returned by TokenRequest
        - request: CallRequest ID
    """

    def dispatch(self, request, *args, **kwargs):
        print(request.GET)

        try:
            manager = get_object_or_404(CallbackManager, pk=Signer().unsign(request.GET.get('manager', 0)))
        except (BadSignature, CallbackManager.DoesNotExist):
            raise PermissionDenied

        callback_request = get_object_or_404(CallbackRequest, pk=request.GET.get('request'))
        entry = CallEntry.objects.create(manager=manager, state='direct', request=callback_request)

        phone = callback_request.right_phone

        resp = Response()
        dial = resp.dial(callerId=settings.TWILIO_DEFAULT_FROM, record=True)
        dial.number(phone,
                    statusCallback=get_full_url(reverse('callback_caller:direct_result',
                                                        args=(Signer().sign(entry.pk),))),
                    statusCallbackMethod='GET')

        return HttpResponse(str(resp), content_type='text/xml')


class DirectCallResult(View):
    """
    View is called by Twilio, when direct call has ended.
    """

    def dispatch(self, request, *args, **kwargs):
        print(request.GET)
        call_entry = get_call_request(CallEntry, **kwargs)

        status = request.GET['CallStatus']

        if status == 'completed':
            call_entry.record_url = request.GET.get('RecordingUrl', None)
            call_entry.duration = request.GET.get('RecordingDuration', 0)
            call_entry.success()
        elif status == 'no-answer':
            call_entry.state = 'no-answer'
            call_entry.save()
        else:
            raise Exception('Unknown status: {}'.format(status))

        return HttpResponse('OK')
