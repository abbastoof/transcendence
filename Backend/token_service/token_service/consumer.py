import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "token_service.settings")
django.setup()


def start_consumer():
    from token_app.views import CustomTokenObtainPairView

    CustomTokenObtainPairView().start_consumer()


if __name__ == "__main__":
    start_consumer()
