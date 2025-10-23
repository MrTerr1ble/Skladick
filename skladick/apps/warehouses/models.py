from django.db import models


class Warehouse(models.Model):
    """Склад (физическая площадка)."""
    code = models.CharField("Код", max_length=32, unique=True)
    name = models.CharField("Название", max_length=128)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Location(models.Model):
    """Место хранения на складе."""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="Склад")
    code = models.CharField("Код", max_length=64)
    name = models.CharField("Название", max_length=128)

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"
        unique_together = ("warehouse", "code")
        ordering = ["warehouse__name", "code"]

    def __str__(self):
        return f"{self.warehouse}:{self.code}"
