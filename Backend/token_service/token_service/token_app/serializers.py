from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import asyncio

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user) -> dict:

        """
            Get token method to generate tokens for the user.

            This method overrides the get_token method of TokenObtainPairSerializer to generate tokens for the user.
            It generates the tokens for the user and returns the tokens.

            Args:
                user: The user object.

            Returns:
                dict: The dictionary containing the tokens.
        """
        token = super().get_token(user)
        token["custom_claims"] = {"username": user.username, "password": user.password}
        return token
