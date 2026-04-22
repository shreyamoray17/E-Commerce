from django.apps import AppConfig


class ModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'models'
    
    def ready(self):
        # Import models to ensure they're registered
        from models import users, products, orders, payments
        # Import admin to register models with admin site
        from models import admin
