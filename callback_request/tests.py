from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.test import APITestCase

from callback_request.models import CallbackRequest, CallEntry
from callback_schedule.models import CallbackManager, CallbackManagerSchedule, CallbackManagerPhone


class CallbackRequestTest(APITestCase):
    def test_callback_request_later(self):
        response = self.client.post('/api/callback/create.json', {
            'name': 'Test',
            'phone': '+1 (234) 56-78-90',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 400, 'Shouldn\'t succeed without comment')

        response = self.client.post('/api/callback/create.json', {
            'name': 'Test',
            'comment': 'Anytime',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 400, 'Shouldn\'t succeed without phone')

        response = self.client.post('/api/callback/create.json', {
            'phone': '+1 (234) 56-78-90',
            'comment': 'Anytime',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/callback/create.json', {
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
        with self.settings(CALLER_FUNCTION='callback_caller.utils.make_stub_call'):
            response = self.client.post('/api/callback/create.json', {
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

            response = self.client.post('/api/callback/create.json', {
                'phone': '+1 (234) 56-78-90',
                'immediate': True,
            })
            self.assertEqual(response.status_code, 201)

            self.assertEqual(CallbackRequest.objects.get(pk=response.data['id']).phones.all().count(), 1)

    def test_call_entries(self):
        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)
        today = now()
        CallbackManagerSchedule.objects.create(manager=manager, weekday=today.weekday(),
                                               available_from='00:00:00',
                                               available_till='23:59:59')
        CallbackManagerPhone.objects.create(manager=manager, phone_type='phone', number='+12345')
        CallbackManagerPhone.objects.create(manager=manager, phone_type='phone', number='+12346', priority=1)

        with self.settings(CALLER_FUNCTION='callback_caller.utils.make_stub_call'):
            self.client.post('/api/callback/create.json', {
                'phone': '+1 (234) 56-78-90',
                'immediate': True,
            })

            self.assertEqual(1, CallEntry.objects.all().count())

            entry_1 = CallEntry.objects.all()[0]
            entry_1.fail()
            self.assertEqual('failed', entry_1.state)

            self.assertEqual(2, CallEntry.objects.all().count())
            entry_2 = CallEntry.objects.get(state='processing')
            entry_2.fail()
            self.assertEqual(2, CallEntry.objects.all().count())

            self.client.post('/api/callback/create.json', {
                'phone': '+1 (234) 56-78-90',
                'immediate': True,
            })
            self.assertEqual(1, CallEntry.objects.filter(state='processing').count())
            entry_3 = CallEntry.objects.get(state='processing')
            entry_3.success()
            self.assertEqual(0, CallEntry.objects.filter(state='processing').count())

    def test_nearest_date(self):
        response = self.client.get('/api/callback/availability.json')
        self.assertEqual({'available': False, 'nearest': None}, response.data)

        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)
        CallbackManagerPhone.objects.create(manager=manager, phone_type='phone', number='+12345')

        today = now().replace(second=0, microsecond=0)
        print('TODAY', today)
        CallbackManagerSchedule.objects.create(manager=manager, weekday=(today.weekday() + 1) % 7,
                                               available_from='12:00:00',
                                               available_till='15:00:00')

        response = self.client.get('/api/callback/availability.json')
        self.assertEqual({'available': False,
                          'nearest': (today.replace(hour=12, minute=0) + timedelta(days=1)).isoformat()[:-6] + 'Z'},
                         response.data)

        CallbackManagerSchedule.objects.create(manager=manager, weekday=today.weekday(),
                                               available_from='00:00:00',
                                               available_till='23:59:59')
        response = self.client.get('/api/callback/availability.json')
        self.assertEqual({'available': True}, response.data)
