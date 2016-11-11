from rest_framework import serializers

from callback_request.models import CallbackRequest


class CallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = ('id', 'phone', 'name', 'comment', 'immediate')

    def validate(self, data):
        immediate = data['immediate']
        if not immediate and not data.get('comment', None):
            raise serializers.ValidationError('Enter comment')
        return data
