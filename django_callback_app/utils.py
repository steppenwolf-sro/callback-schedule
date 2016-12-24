from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework import serializers


class ProtectedPermission(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.change_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class CallbackUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = 'first_name', 'last_name', 'email', 'id'
