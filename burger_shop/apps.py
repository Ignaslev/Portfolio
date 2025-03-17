from django.apps import AppConfig


class BurgerShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'burger_shop'

    def ready(self):
        import burger_shop.signals