from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView

from callback_schedule.models import CallbackManager, CallbackManagerSchedule
from callback_schedule.serializers import CMSerializer, CMScheduleSerializer


class ProtectedPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        super().__init__()
        self.perms_map['GET'] = ['%(app_label)s.change_%(model_name)s']

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return super().has_permission(request, view)


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
