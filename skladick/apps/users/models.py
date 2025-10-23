from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь системы."""
    full_name = models.CharField("ФИО", max_length=150, blank=True)
    role = models.CharField(
        "Роль",
        max_length=50,
        choices=[
            ("ADMIN", "Администратор"),
            ("OPERATOR", "Оператор"),
            ("WAREHOUSE", "Кладовщик"),
            ("ANALYST", "Аналитик"),
        ],
        default="OPERATOR"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
