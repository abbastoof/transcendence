from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_app"

    def ready(self) -> None:
        import user_app.signals
