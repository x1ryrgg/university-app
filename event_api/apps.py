from django.apps import AppConfig


class EventApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event_api'

    def ready(self):
        import event_api.signals
