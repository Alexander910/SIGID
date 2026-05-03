from django.apps import AppConfig


class MovimientosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movimientos'
    verbose_name = 'Movimientos'

    def ready(self):
        import movimientos.signals  # noqa: F401
