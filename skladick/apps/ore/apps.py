from django.apps import AppConfig


class OreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ore"
    verbose_name = "Руда (приёмка/отгрузка)"

    def ready(self):
        from . import signals
