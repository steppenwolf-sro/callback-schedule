from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.test import APITestCase

from callback_request.models import CallbackRequest
from callback_schedule.models import CallbackManager, CallbackManagerSchedule, CallbackManagerPhone


class CallbackRequestTest(APITestCase):
    def test_caller(self):
        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)
        today = now()
        CallbackManagerSchedule.objects.create(manager=manager, weekday=today.weekday(),
                                               available_from='00:00:00',
                                               available_till='23:59:59')
        CallbackManagerPhone.objects.create(manager=manager, phone_type='phone', number='+12345')
        CallbackManagerPhone.objects.create(manager=manager, phone_type='phone', number='+12346', priority=1)

        with self.settings(CALLER_FUNCTION='caller.utils.make_stub_success_call'):
            response = self.client.post('/api/callback/create.json', {
                'phone': '+1 (234) 56-78-90',
                'immediate': True,
            })
            request = CallbackRequest.objects.get(pk=response.data['id'])
            self.assertEqual(1, request.callentry_set.filter(state='success').count())

        with self.settings(CALLER_FUNCTION='caller.utils.make_stub_failed_call'):
            response = self.client.post('/api/callback/create.json', {
                'phone': '+1 (234) 56-78-90',
                'immediate': True,
            })
            request = CallbackRequest.objects.get(pk=response.data['id'])
            self.assertEqual(2, request.callentry_set.filter(state='failed').count())
