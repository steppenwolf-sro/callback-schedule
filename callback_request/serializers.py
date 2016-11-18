from rest_framework import serializers

from callback_request.models import CallbackRequest, CallEntry
from callback_schedule.models import CallbackManagerPhone


class CallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = ('id', 'phone', 'name', 'comment', 'immediate')

    def validate(self, data):
        immediate = data['immediate']
        if not immediate and not data.get('comment', None):
            raise serializers.ValidationError('Enter comment')

        if immediate:
            phones = CallbackManagerPhone.get_available_phones()
            if not phones.exists():
                raise serializers.ValidationError('No free managers')
        return data


class CallbackRequestAdminSerializer(CallbackSerializer):
    class Meta:
        model = CallbackRequest
        fields = ('id', 'phone', 'comment', 'client', 'created', 'name', 'completed', 'date', 'right_phone',
                  'immediate')
        read_only_fields = ('id', 'phone', 'comment', 'created', 'name')


class CallEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CallEntry
        fields = '__all__'


class ManagersAvailabilitySerializer(serializers.Serializer):
    available = serializers.BooleanField()
    nearest = serializers.DateTimeField(required=False)
