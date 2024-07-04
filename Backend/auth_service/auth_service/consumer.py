import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_service.settings")
django.setup()


def start_consumer():
    from user_auth.views import CustomTokenObtainPairView

    CustomTokenObtainPairView().start_consumer()


if __name__ == "__main__":
    start_consumer()
