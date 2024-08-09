import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_history.settings")
django.setup()


def start_consumer():
    from game_data.views import GameHistoryViewSet

    GameHistoryViewSet().start_consumer()


if __name__ == "__main__":
    start_consumer()
