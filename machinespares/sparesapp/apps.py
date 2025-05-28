from django.apps import AppConfig


class SparesappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sparesapp'

    def ready(self):
        # Import signals to activate them
        import sparesapp.signals
