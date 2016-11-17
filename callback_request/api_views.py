from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from callback_request.serializers import CallbackSerializer, ManagersAvailabilitySerializer
from callback_schedule.models import CallbackManagerPhone, CallbackManagerSchedule


class CreateCallbackRequest(CreateAPIView):
    serializer_class = CallbackSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated() else None
        if user:
            phone = serializer.validated_data.get('phone', '')
            name = serializer.validated_data.get('name', '')
            if name:
                get_user_model().objects.filter(pk=user.pk).update(first_name=name)
            if phone:
                get_user_model().objects.filter(pk=user.pk).update(phone=phone)

        if serializer.validated_data['immediate']:
            phones = CallbackManagerPhone.get_available_phones()
        else:
            phones = []
        serializer.save(client=user, phones=phones)


class ManagersAvailabilityView(APIView):
    @staticmethod
    def get_nearest_date(start):
        schedules = CallbackManagerSchedule.objects.all()
        if schedules.count() == 0:
            return None

        dates = [start + relativedelta(weekday=item.weekday, hour=item.available_from.hour,
                                       minute=item.available_from.minute)
                 for item in schedules]
        dates += [start + relativedelta(weekday=item.weekday, hour=item.available_from.hour,
                                        days=+1, minute=item.available_from.minute)
                  for item in schedules]
        dates = [date for date in dates if date > start]
        return sorted(dates)[0]

    def get(self, request, *args, **kwargs):
        phones = CallbackManagerPhone.get_available_phones()
        if phones.count():
            data = {
                'available': True
            }
        else:
            data = {
                'available': False,
                'nearest': ManagersAvailabilityView.get_nearest_date(now().replace(second=0, microsecond=0))
            }

        serializer = ManagersAvailabilitySerializer(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
