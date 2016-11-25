from rest_framework import serializers

from callback_schedule.models import CallbackManager, CallbackManagerSchedule, CallbackManagerPhone


class CMScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackManagerSchedule
        fields = 'weekday', 'available_from', 'available_till'


class CMSerializer(serializers.ModelSerializer):
    schedule = CMScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = CallbackManager
        fields = '__all__'


class CMPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackManagerPhone
        fields = 'id', 'phone_type', 'number', 'priority'
