from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User

class UserSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
	class Meta:
		model = User
		fields = ['id', 'username','email', 'password']
		extra_kwargs = {'password': {'write_only': True}}

	def create(self, validate_data):
		password = validate_data.pop('password', None)
		instance = self.Meta.model(**validate_data)
		if password is not None:
			instance.set_password(password)
		instance.save()
		return instance
	
	def update(self, instance, validated_data):
		for attr, value in validated_data.items():
			if attr == 'password' and value is not None:
				instance.set_password(value)
			else:
				setattr(instance, attr, value)
		instance.save()
		return instance


