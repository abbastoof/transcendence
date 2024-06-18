from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User
from .validators import CustomPasswordValidator

class UserSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
	class Meta:
		model = User
		fields = ['id', 'username','email', 'password']
		extra_kwargs = {'password': {'write_only': True}}

		### Password should be strong password, minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character


	def create(self, validate_data):
		try:
			validate_password(validate_data['password'])
		except ValidationError as err:
			raise serializers.ValidationError({'password': err.messages})
		password = validate_data.pop('password', None)
		instance = self.Meta.model(**validate_data)
		if password is not None:
			instance.set_password(password)
		instance.save()
		return instance
	
	def update(self, instance, validate_data):
		for attr, value in validate_data.items():
			if attr == 'password' and value is not None:
				if instance.check_password(value):
					raise serializers.ValidationError({'password': 'New password must be different from the current password.'})

				# Validate the new password using CustomPasswordValidator
				try:
					validator = CustomPasswordValidator()
					validator.validate(value, user=instance)
				except ValidationError as err:
					raise serializers.ValidationError({'password': err.messages})
				instance.set_password(value)
			else:
				setattr(instance, attr, value)
		instance.save()
		return instance