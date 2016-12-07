from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.test import APITestCase

from callback_request.api_views import ManagersAvailabilityView
from callback_request.models import CallbackRequest, CallEntry
from callback_schedule.models import CallbackManager, CallbackManagerSchedule, CallbackManagerPhone


class CallbackRequestTest(APITestCase):
    def test_api_requests_manager(self):
        today = now()
        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)
        CallbackManagerSchedule.objects.create(manager=manager, weekday=(today + timedelta(days=1)).weekday(),
                                               available_from="00:00", available_till="23:59")

        response = self.client.post('/api/callback/create.json', {
            'phone': '+1 (234) 56-78-90',
            'date': (today + timedelta(days=1)).isoformat(),
            'immediate': False,
        })
        pk = response.data['id']
        print('We have created request')

        response = self.client.get('/api/callback/manage/requests.json')
        self.assertEqual(403, response.status_code)
        print('> Unauthorized user can\'t get requests list')

        response = self.client.get('/api/callback/manage/requests/{}.json'.format(pk))
        self.assertEqual(403, response.status_code)
        print('> Unauthorized user can\'t get request')

        admin = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'test')
        self.client.force_authenticate(admin)
        print('Logged in as superuser')
        response = self.client.get('/api/callback/manage/requests.json')
        self.assertEqual(200, response.status_code)
        print('> Admin can get requests list')

        response = self.client.get('/api/callback/manage/requests/{}.json'.format(pk))
        self.assertEqual(200, response.status_code)
        print('> Admin can get request')

        self.client.force_authenticate(None)

    def test_callback_request_later(self):
        today = now()
        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)
        CallbackManagerSchedule.objects.create(manager=manager, weekday=(today + timedelta(days=1)).weekday(),
                                               available_from="00:00", available_till="23:59")
        response = self.client.post('/api/callback/create.json', {
            'name': 'Test',
            'phone': '+1 (234) 56-78-90',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 400, 'Shouldn\'t succeed without date')

        response = self.client.post('/api/callback/create.json', {
            'name': 'Test',
            'immediate': False,
        })
        self.assertEqual(response.status_code, 400, 'Shouldn\'t succeed without phone')

        response = self.client.post('/api/callback/create.json', {
            'phone': '+1 (234) 56-78-90',
            'date': (today + timedelta(days=1)).isoformat(),
            'immediate': False,
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/callback/create.json', {
            'name': 'Test',
            'phone': '+1 (234) 56-78-90',
            'date': (today + timedelta(days=1)).isoformat(),
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

            self.assertEqual(CallEntry.objects.all().count(), 1)

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

            self.assertEqual(2, CallEntry.objects.all().count())

            entry_1 = CallEntry.objects.all()[0]
            entry_1.fail()
            self.assertEqual('failed', entry_1.state)

            self.assertEqual(2, CallEntry.objects.all().count())
            entry_2 = CallEntry.objects.get(state='waiting')
            entry_2.fail()
            self.assertEqual(2, CallEntry.objects.all().count())

            self.client.post('/api/callback/create.json', {
                'phone': '+1 (234) 56-78-90',
                'immediate': True,
            })
            self.assertEqual(2, CallEntry.objects.filter(state='waiting').count())
            entry_3 = CallEntry.objects.filter(state='waiting')[0]
            entry_3.success()
            self.assertEqual(0, CallEntry.objects.filter(state='processing').count())

    def test_real_schedule(self):
        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)

        today = datetime(2016, 11, 23, 12, 0)  # Wednesday

        CallbackManagerSchedule.objects.create(manager=manager, weekday=0,
                                               available_from='12:00:00', available_till='12:30:00')

        CallbackManagerSchedule.objects.create(manager=manager, weekday=3,
                                               available_from='13:00:00', available_till='13:30:00')

        CallbackManagerSchedule.objects.create(manager=manager, weekday=3,
                                               available_from='13:00:00', available_till='13:20:00')

        CallbackManagerSchedule.objects.create(manager=manager, weekday=2,
                                               available_from='10:00:00', available_till='12:30:00')

        schedule = ManagersAvailabilityView.get_real_schedule(today)
        self.assertEqual(
            [
                datetime(2016, 11, 23, 12, 10),
                datetime(2016, 11, 23, 12, 20),
                datetime(2016, 11, 24, 13, 0),
                datetime(2016, 11, 24, 13, 10),
                datetime(2016, 11, 24, 13, 20),
                datetime(2016, 11, 28, 12, 0),
                datetime(2016, 11, 28, 12, 10),
                datetime(2016, 11, 28, 12, 20),
            ],
            schedule
        )

    def test_nearest_date(self):
        response = self.client.get('/api/callback/availability.json')
        self.assertEqual({'available': False, 'nearest': None, 'schedule': []}, response.data)

        user = get_user_model().objects.create_user('Manager#1')
        manager = CallbackManager.objects.create(user=user)
        CallbackManagerPhone.objects.create(manager=manager, phone_type='phone', number='+12345')

        today = now().replace(second=0, microsecond=0)
        print('TODAY', today)
        CallbackManagerSchedule.objects.create(manager=manager, weekday=(today.weekday() + 1) % 7,
                                               available_from='12:00:00',
                                               available_till='12:30:00')

        response = self.client.get('/api/callback/availability.json')
        self.assertEqual({'available': False,
                          'nearest': (today.replace(hour=12, minute=0) + timedelta(days=1)).isoformat()[:-6] + 'Z',
                          'schedule': [
                              (today.replace(hour=12, minute=0) + timedelta(days=1)).isoformat()[:-6] + 'Z',
                              (today.replace(hour=12, minute=10) + timedelta(days=1)).isoformat()[:-6] + 'Z',
                              (today.replace(hour=12, minute=20) + timedelta(days=1)).isoformat()[:-6] + 'Z',
                          ]},
                         response.data)

        CallbackManagerSchedule.objects.create(manager=manager, weekday=today.weekday(),
                                               available_from='00:00:00',
                                               available_till='23:59:59')
        response = self.client.get('/api/callback/availability.json')
        self.assertEqual(True, response.data['available'])
