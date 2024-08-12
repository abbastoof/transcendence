import os
import asyncio
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "token_service.settings")
django.setup()


async def start_consumer():
    from token_app.views import CustomTokenObtainPairView, ValidateToken, InvalidateToken
    await CustomTokenObtainPairView().start_consumer()

    await asyncio.gather(
        CustomTokenObtainPairView().start_consumer(),
        ValidateToken().start_consumer(),
        InvalidateToken().start_consumer()
    )

if __name__ == "__main__":
    asyncio.run(start_consumer())
