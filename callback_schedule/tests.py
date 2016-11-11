import datetime

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from callback_schedule.models import CallbackManager


class CallbackTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin', 'admin@example.com', 'test')

    def test_manager_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/ru/api/callback/managers.json')
        self.assertEqual(response.data, [])

        response = self.client.post('/ru/api/callback/managers.json', {'user': self.admin.pk})
        self.assertEqual(CallbackManager.objects.all().count(), 1)
        manager_pk = response.data['id']

        response = self.client.post('/ru/api/callback/managers/{}/schedule.json'.format(manager_pk), {
            'weekday': 0,
            'available_from': datetime.time(12, 0),
            'available_till': datetime.time(15, 0),
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/ru/api/callback/managers.json')
        self.assertEqual(response.data[0]['schedule'], [{
            'weekday': 0,
            'available_from': '12:00:00',
            'available_till': '15:00:00',
        }])

        user = User.objects.create_user('user')
        response = self.client.post('/ru/api/callback/managers.json', {'user': user.pk, 'priority': 1})
        manager_2_pk = response.data['id']
        self.assertEqual(CallbackManager.objects.all().count(), 2)
        response = self.client.post('/ru/api/callback/managers/{}/schedule.json'.format(manager_2_pk), {
            'weekday': 0,
            'available_from': datetime.time(13, 0),
            'available_till': datetime.time(16, 0),
        })
        self.assertEqual(response.status_code, 201)

        friday_12 = datetime.datetime(2016, 11, 11, 12, 0)
        monday_13 = datetime.datetime(2016, 11, 14, 13, 0)
        monday_15_30 = datetime.datetime(2016, 11, 14, 15, 30)
        monday_12_30 = datetime.datetime(2016, 11, 14, 12, 30)

        # No manager should be available on Friday 12:00
        self.assertEqual(CallbackManager.get_available_managers(friday_12).count(), 0)

        # Manager 2 should be available on Monday 13:00, because he has a greater priority
        self.assertEqual(CallbackManager.get_available_managers(monday_13)[0].pk, manager_2_pk)

        # Manager 2 should be available on Monday 15:30, because only he is available at this time
        self.assertEqual(CallbackManager.get_available_managers(monday_15_30)[0].pk, manager_2_pk)

        # Manager 1 should be available on Monday 12:30, because only he is available at this time
        self.assertEqual(CallbackManager.get_available_managers(monday_12_30)[0].pk, manager_pk)
