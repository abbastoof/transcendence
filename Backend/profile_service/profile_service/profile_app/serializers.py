from rest_framework import serializers
from .models import UserTokens

class UserTokenModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTokens
        fields = "__all__"