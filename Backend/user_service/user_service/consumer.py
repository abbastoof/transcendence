import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_service.settings")
django.setup()


def start_consumer():
    from user_app.views import UserViewSet

    UserViewSet().start_consumer()


if __name__ == "__main__":
    start_consumer()
