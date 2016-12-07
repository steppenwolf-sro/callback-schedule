from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers

from callback_request.models import CallbackRequest, CallEntry
from callback_schedule.models import CallbackManagerPhone


class CallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = ('id', 'phone', 'name', 'date', 'immediate')

    def validate(self, data):
        immediate = data.get('immediate', False)
        if not immediate and not data.get('date', None):
            raise serializers.ValidationError('Enter date')

        if immediate:
            phones = CallbackManagerPhone.get_available_phones()
            if len(phones) == 0:
                raise serializers.ValidationError('No free managers')
        return data


class CallbackRequestAdminSerializer(serializers.ModelSerializer):
    client = import_string(settings.CALLBACK_CLIENT_SERIALIZER)(read_only=True)

    class Meta:
        model = CallbackRequest
        fields = ('id', 'phone', 'comment', 'client', 'created', 'name', 'completed', 'date', 'right_phone',
                  'immediate')
        read_only_fields = ('id', 'phone', 'comment', 'created', 'name', 'immediate', 'client')


class CallEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CallEntry
        fields = '__all__'


class ManagersAvailabilitySerializer(serializers.Serializer):
    available = serializers.BooleanField()
    nearest = serializers.DateTimeField(required=False)
    schedule = serializers.ListSerializer(child=serializers.DateTimeField())
