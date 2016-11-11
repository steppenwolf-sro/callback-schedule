from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from callback_request.serializers import CallbackSerializer


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
