import datetime

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from callback_schedule.models import CallbackManager, CallbackManagerPhone, CallbackManagerSchedule


class CallbackTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin', 'admin@example.com', 'test')

    def test_available_phones(self):
        manager = CallbackManager.objects.create(user=self.admin)
        ph1 = CallbackManagerPhone.objects.create(manager=manager, phone_type='test', number='000', priority=0)
        ph2 = CallbackManagerPhone.objects.create(manager=manager, phone_type='test', number='111', priority=1)
        ph3 = CallbackManagerPhone.objects.create(manager=manager, phone_type='test', number='222', priority=1)
        ph4 = CallbackManagerPhone.objects.create(manager=manager, phone_type='test', number='333', priority=2)

        CallbackManagerSchedule.objects.create(manager=manager, weekday=0,
                                               available_from=datetime.time(0, 0),
                                               available_till=datetime.time(23, 59))

        date = datetime.datetime(2016, 11, 28)  # Monday

        phones_set = CallbackManagerPhone.get_available_phones(date)
        self.assertEqual(
            [[ph1.pk], [ph2.pk, ph3.pk], [ph4.pk]],
            [[x.pk for x in phones] for phones in phones_set]
        )

    def test_manager_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/callback/managers.json')
        self.assertEqual(response.data, [])

        response = self.client.post('/api/callback/managers.json', {'user': self.admin.pk})
        self.assertEqual(CallbackManager.objects.all().count(), 1)
        manager_pk = response.data['id']
        CallbackManagerPhone.objects.create(manager=CallbackManager.objects.get(pk=manager_pk), phone_type='test',
                                            number='123456', priority=1)

        response = self.client.post('/api/callback/managers/{}/schedule.json'.format(manager_pk), {
            'weekday': 0,
            'available_from': datetime.time(12, 0),
            'available_till': datetime.time(15, 0),
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/callback/managers.json')
        self.assertEqual(response.data[0]['schedule'], [{
            'weekday': 0,
            'available_from': '12:00:00',
            'available_till': '15:00:00',
        }])

        user = User.objects.create_user('user')
        response = self.client.post('/api/callback/managers.json', {'user': user.pk})
        manager_2_pk = response.data['id']
        CallbackManagerPhone.objects.create(manager=CallbackManager.objects.get(pk=manager_2_pk), phone_type='test',
                                            number='234567')
        self.assertEqual(CallbackManager.objects.all().count(), 2)
        response = self.client.post('/api/callback/managers/{}/schedule.json'.format(manager_2_pk), {
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
        self.assertEqual(len(CallbackManagerPhone.get_available_phones(friday_12)), 0)

        # Manager 2 should be available on Monday 13:00, because he has a greater priority
        self.assertEqual(CallbackManagerPhone.get_available_phones(monday_13)[0][0].manager.pk, manager_2_pk)

        # Manager 2 should be available on Monday 15:30, because only he is available at this time
        self.assertEqual(CallbackManagerPhone.get_available_phones(monday_15_30)[0][0].manager.pk, manager_2_pk)

        # Manager 1 should be available on Monday 12:30, because only he is available at this time
        self.assertEqual(CallbackManagerPhone.get_available_phones(monday_12_30)[0][0].manager.pk, manager_pk)
