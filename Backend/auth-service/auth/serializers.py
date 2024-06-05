from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}} # extra_kwargs is a dictionary that allows us to specify some extra attributes for the fields in the User model

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data) # create_user is a method in the User model
        return user

    def update(self, instance, validated_data): # update method is used to update an existing user object
        instance.username = validated_data.get('username', instance.username)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance
