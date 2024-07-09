import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "profile_service.settings")
django.setup()


def start_consumer():
    from profile_app.views import ValidateToken

    ValidateToken().start_consumer()


if __name__ == "__main__":
    start_consumer()
