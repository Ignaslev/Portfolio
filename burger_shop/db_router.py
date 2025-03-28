

class BurgerShopRouter:
    app_label = 'burger_shop'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'default'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == 'default'
        return db == 'default'
