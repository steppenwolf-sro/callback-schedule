from rest_framework import serializers

from callback_request.models import CallbackRequest
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
