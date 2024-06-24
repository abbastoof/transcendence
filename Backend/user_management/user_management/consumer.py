import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_management.settings")
django.setup()


def start_consumer():
    from users.views import UserViewSet

    UserViewSet().start_consumer()


if __name__ == "__main__":
    start_consumer()
