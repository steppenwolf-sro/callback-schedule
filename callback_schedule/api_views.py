from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView, ListAPIView

from callback_schedule.models import CallbackManager, CallbackManagerSchedule, CallbackManagerPhone
from callback_schedule.serializers import CMSerializer, CMScheduleSerializer, CMPhoneSerializer
from django_callback_app.utils import ProtectedPermission


class CallbackManagerList(ListCreateAPIView):
    serializer_class = CMSerializer
    permission_classes = [ProtectedPermission]
    queryset = CallbackManager.objects.all()


class ScheduleList(ListCreateAPIView):
    serializer_class = CMScheduleSerializer
    permission_classes = [ProtectedPermission]

    def get_queryset(self):
        return CallbackManagerSchedule.objects.filter(manager__pk=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(manager=CallbackManager.objects.get(pk=self.kwargs['pk']))


class MyPhoneList(ListAPIView):
    serializer_class = CMPhoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CallbackManagerPhone.objects.filter(manager__user__pk=self.request.user.pk)
