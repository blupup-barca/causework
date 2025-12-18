from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {"blank": True, "null": True}


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="почта", help_text="Введите почту"
    )
    first_name = models.CharField(
        max_length=50, verbose_name="Имя", help_text="Введите имя", **NULLABLE
    )
    last_name = models.CharField(
        max_length=50, verbose_name="Фамилия", help_text="Введите фамилию", **NULLABLE
    )
    tg_chat_id = models.CharField(
        max_length=50,
        verbose_name="ID чата в Telegram",
        help_text="Укажите ID чата в Telegram",
        **NULLABLE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
