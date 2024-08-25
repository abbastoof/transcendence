from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import UserProfileModel, FriendRequest, GameRoom, ConfirmEmail
from .validators import CustomPasswordValidator

class GameRoomSerializer(serializers.ModelSerializer):
    player1_id = serializers.SerializerMethodField()
    player2_id = serializers.SerializerMethodField()
    player1_username = serializers.SerializerMethodField()
    player2_username = serializers.SerializerMethodField()
    class Meta:
        model = GameRoom
        fields = "__all__"

    def get_player1_id(self, obj):
        return obj.player1.id if obj.player1 else None

    def get_player2_id(self, obj):
        return obj.player2.id if obj.player2 else None

    def get_player1_username(self, obj):
        return obj.player1.username if obj.player1 else None

    def get_player2_username(self, obj):
        return obj.player2.username if obj.player2 else None


class FriendSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender_user.id")
    receiver_id = serializers.IntegerField(source="receiver_user.id")
    sender_username = serializers.SerializerMethodField()
    receiver_username = serializers.SerializerMethodField()
    class Meta:
        model=FriendRequest
        fields = ["sender_id", "sender_username", "receiver_id", "receiver_username", "status"]

    def get_sender_username(self, obj):
        return obj.sender_user.username

    def get_receiver_username(self, obj):
        return obj.receiver_user.username


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
    email = serializers.PrimaryKeyRelatedField(queryset=ConfirmEmail.objects.all())
    avatar = serializers.ImageField(required=False)
    friends = serializers.PrimaryKeyRelatedField(
        many=True, queryset=UserProfileModel.objects.all(), required=False # required=False means that the field is not required
    )

    class Meta:
        model = UserProfileModel
        fields = [
            "id",
            "username",
            "email",
            "password",
            "avatar",
            "online_status",
            "friends",
            "otp_status",
            "otp",
            "otp_expiry_time"
            ]
        extra_kwargs = {"password": {"write_only": True}}
        ### Password should be strong password, minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character

    def create(self, validated_data) -> UserProfileModel:
        """
            Method to create a new user.

            This method creates a new user with the given data.
            The password is validated using CustomPasswordValidator.
            The password is hashed before saving the user object.
            Args:
                validated_data: The data to validate.

            Returns:
                User: The user object.
        """
        try:
            validate_password(validated_data["password"])
        except ValidationError as err:
            raise serializers.ValidationError(detail=err.messages) from err
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data) -> UserProfileModel:
        """
            Method to update a user.

            This method updates a user with the given data.
            The password is hashed before saving the user object.

            Args:
                instance: The user object.
                validated_data: The data to validate.

            Returns:
                User: The updated user object.

            Raises:
                serializers.ValidationError: If the password is the same as the current password.

        """
        for attr, value in validated_data.items(): # Iterate over the validated data and update the user object
            if attr == "password" and value is not None: # Check if the attribute is password and the value is not None (i.e., the password is being updated)
                if instance.check_password(value): # Check if the new password is the same as the current password (i.e., the user is trying to set the same password)
                    raise serializers.ValidationError(detail="New password must be different from the current password.")

                # Validate the new password using CustomPasswordValidator
                try:
                    validator = CustomPasswordValidator() # Create an instance of CustomPasswordValidator
                    validator.validate(value, user=instance) # Validate the new password using CustomPasswordValidator
                except ValidationError as err:
                    raise serializers.ValidationError(detail=err.messages) from err
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

class ConfirmEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmEmail
        fields = '__all__'
