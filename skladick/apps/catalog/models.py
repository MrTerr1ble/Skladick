from django.db import models


class Uom(models.Model):
    code = models.CharField("Код", max_length=16, unique=True, db_index=True)
    name = models.CharField("Название", max_length=64)

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ["code"]

    def __str__(self):
        return self.code


class Item(models.Model):
    sku = models.CharField("Артикул", max_length=64, unique=True, db_index=True)
    name = models.CharField("Наименование", max_length=128)
    description = models.TextField("Описание", blank=True)
    base_uom = models.ForeignKey(Uom, on_delete=models.PROTECT, verbose_name="Базовая ЕИ")

    class Meta:
        verbose_name = "Номенклатура"
        verbose_name_plural = "Номенклатура"
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"{self.sku} — {self.name}"


class Supplier(models.Model):
    code = models.CharField("Код", max_length=32, unique=True)
    name = models.CharField("Наименование", max_length=256)
    tax_id = models.CharField("ИНН/Tax ID", max_length=64, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}"