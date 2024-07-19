from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, FriendRequest
from .validators import CustomPasswordValidator


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model=FriendRequest
        fields = ["sender_user", "receiver_user", "status"]
class UserSerializer(serializers.ModelSerializer):
    """
        UserSerializer class to define the user serializer.

        This class defines the user serializer to serialize the user data.

        Attributes:
            email: The email field.
            Meta: The meta class to define the model and fields for the serializer.

            Methods:
                create: Method to create a new user.
                update: Method to update a user.
    """
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    friends = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False # required=False means that the field is not required
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "avatar", "status", "friends"]
        extra_kwargs = {"password": {"write_only": True}}

        ### Password should be strong password, minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character

    def create(self, validate_data) -> User:
        """
            Method to create a new user.

            This method creates a new user with the given data.
            The password is validated using CustomPasswordValidator.
            The password is hashed before saving the user object.
            Args:
                validate_data: The data to validate.

            Returns:
                User: The user object.
        """
        try:
            validate_password(validate_data["password"])
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages}) from err
        password = validate_data.pop("password", None)
        instance = self.Meta.model(**validate_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validate_data) -> User:
        """
            Method to update a user.

            This method updates a user with the given data.
            The password is hashed before saving the user object.

            Args:
                instance: The user object.
                validate_data: The data to validate.

            Returns:
                User: The updated user object.

            Raises:
                serializers.ValidationError: If the password is the same as the current password.

        """
        for attr, value in validate_data.items():
            if attr == "password" and value is not None:
                if instance.check_password(value):
                    raise serializers.ValidationError(
                        {
                            "password": "New password must be different from the current password."
                        }
                    )

                # Validate the new password using CustomPasswordValidator
                try:
                    validator = CustomPasswordValidator()
                    validator.validate(value, user=instance)
                except ValidationError as err:
                    raise serializers.ValidationError(
                        {"password": err.messages}
                    ) from err
                instance.set_password(value)
            # if attr == "friends" and value is not None:
            #     friends_list = instance.friends
            #     for friend in value:
            #         friends_list.append(friend)
            #     instance.friends.set(friends_list)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
