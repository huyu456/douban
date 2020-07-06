from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'user'
    verbose_name = "用户管理"

    def ready(self):
        import user.signals
