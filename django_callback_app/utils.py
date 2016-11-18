from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework import serializers


class ProtectedPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        super().__init__()
        self.perms_map['GET'] = ['%(app_label)s.change_%(model_name)s']

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return super().has_permission(request, view)


class CallbackUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = 'first_name', 'last_name', 'email', 'id'
