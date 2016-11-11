from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.test import APITestCase

from callback_request.models import CallbackRequest
from callback_schedule.models import CallbackManager, CallbackManagerSchedule, CallbackManagerPhone


class CallbackRequestTest(APITestCase):
    def test_callback_request_later(self):
        response = self.client.post('/ru/api/callback/create.json', {
            'name': 'Test',
            'phone': '+1 (234) 56-78-90',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 400, 'Shouldn\'t succeed without comment')

        response = self.client.post('/ru/api/callback/create.json', {
            'name': 'Test',
            'comment': 'Anytime',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 400, 'Shouldn\'t succeed without phone')

        response = self.client.post('/ru/api/callback/create.json', {
            'phone': '+1 (234) 56-78-90',
            'comment': 'Anytime',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/ru/api/callback/create.json', {
            'name': 'Test',
            'phone': '+1 (234) 56-78-90',
            'comment': 'Anytime',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 201)

        request_id = response.data['id']
        request = CallbackRequest.objects.get(pk=request_id)
        self.assertEqual(request.right_phone, '+1234567890')

    def test_callback_request_now(self):
        response = self.client.post('/ru/api/callback/create.json', {
            'phone': '+1 (234) 56-78-90',
            'immediate': True,
        })
        self.assertEqual(response.status_code, 400, 'No free managers, shouldn\'t accept request')

        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)
        today = now()
        CallbackManagerSchedule.objects.create(manager=manager, weekday=today.weekday(),
                                               available_from='00:00:00',
                                               available_till='23:59:59')
        CallbackManagerPhone.objects.create(manager=manager, phone_type='phone', number='+12345')

        response = self.client.post('/ru/api/callback/create.json', {
            'phone': '+1 (234) 56-78-90',
            'immediate': True,
        })
        self.assertEqual(response.status_code, 201)

        self.assertEqual(CallbackRequest.objects.get(pk=response.data['id']).managers.all().count(), 1)

        # self.assertEqual(CallEntry.objects.filter(request__id=response.data['id']).count(), 1)
