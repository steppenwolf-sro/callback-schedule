from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MINUTELY
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from callback_request.models import CallbackRequest, CallEntry
from callback_request.serializers import CallbackSerializer, ManagersAvailabilitySerializer, \
    CallbackRequestAdminSerializer, CallEntrySerializer
from callback_schedule.models import CallbackManagerPhone, CallbackManagerSchedule
from django_callback_app.utils import ProtectedPermission


class Pagination(PageNumberPagination):
    page_size = 20


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

        serializer.save(client=user)


class CallbackRequestAdminView(ListAPIView):
    queryset = CallbackRequest.objects.all().extra(
        select={'null_date': 'date is null'}
    ).order_by('completed', '-null_date', 'date', '-created')
    serializer_class = CallbackRequestAdminSerializer
    permission_classes = [ProtectedPermission]
    pagination_class = Pagination


class CallbackRequestAdminDetailView(RetrieveUpdateAPIView):
    serializer_class = CallbackRequestAdminSerializer
    permission_classes = [ProtectedPermission]
    queryset = CallbackRequest.objects.all()


class CallEntryList(ListAPIView):
    serializer_class = CallEntrySerializer
    permission_classes = [ProtectedPermission]

    def get_queryset(self):
        return CallEntry.objects.filter(request__pk=self.kwargs['pk']).order_by('-created')


class ManagersAvailabilityView(APIView):
    @staticmethod
    def get_real_schedule(start=None):
        start = start or now().replace(second=0, microsecond=0)
        result = set()
        for schedule in CallbackManagerSchedule.objects.all():
            set_start = start + relativedelta(weekday=schedule.weekday)
            current = set(
                rrule(
                    MINUTELY,
                    dtstart=set_start.replace(
                        hour=schedule.available_from.hour,
                        minute=schedule.available_from.minute
                    ),
                    interval=10,
                    until=set_start.replace(
                        hour=schedule.available_till.hour,
                        minute=schedule.available_till.minute
                    ) - relativedelta(seconds=1)
                )
            )
            result = result.union(current)
        return sorted([n for n in result if n > start])

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
        if len(phones) > 0:
            data = {
                'available': True
            }
        else:
            data = {
                'available': False,
                'nearest': ManagersAvailabilityView.get_nearest_date(now().replace(second=0, microsecond=0))
            }

        data['schedule'] = self.get_real_schedule()
        serializer = ManagersAvailabilitySerializer(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
