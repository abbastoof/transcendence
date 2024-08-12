import os
import asyncio
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_history.settings")
django.setup()


async def start_consumer():
    from game_data.views import start_consumer

    await start_consumer()


if __name__ == "__main__":
    asyncio.run(start_consumer())
