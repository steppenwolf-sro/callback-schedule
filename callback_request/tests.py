from rest_framework.test import APITestCase

from callback_request.models import CallbackRequest


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
