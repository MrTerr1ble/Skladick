from django.db import models


class TransportUnit(models.Model):
    """Транспортная единица: авто/вагон и т.п."""
    TRUCK, TRAIN, SHIP, OTHER = "TRUCK", "TRAIN", "SHIP", "OTHER"
    TYPES = [(TRUCK, "Авто"), (TRAIN, "ЖД"), (SHIP, "Судно"), (OTHER, "Другое")]

    type = models.CharField("Тип", max_length=8, choices=TYPES, default=TRUCK)
    number = models.CharField("Номер", max_length=32, db_index=True)

    class Meta:
        verbose_name = "Транспорт"
        verbose_name_plural = "Транспорт"
        unique_together = ("type", "number")
        ordering = ["type", "number"]

    def __str__(self):
        return f"{self.get_type_display()} {self.number}"


class Arrival(models.Model):
    """Прибытие транспорта (поставка)."""
    unit = models.ForeignKey(TransportUnit, on_delete=models.PROTECT, verbose_name="Транспорт")
    route_no = models.CharField("Рейс/маршрут", max_length=32, blank=True)
    arrived_at = models.DateTimeField("Прибытие")

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"
        ordering = ["-arrived_at"]

    def __str__(self):
        return f"{self.unit} @ {self.arrived_at:%Y-%m-%d %H:%M}"


class ArrivalLine(models.Model):
    """Состав поставки по позициям."""
    arrival = models.ForeignKey(Arrival, on_delete=models.CASCADE, related_name="lines", verbose_name="Поставка")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    qty = models.DecimalField("Кол-во", max_digits=18, decimal_places=3)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="ЕИ")
    location = models.ForeignKey("warehouses.Location", on_delete=models.PROTECT, verbose_name="Локация назначения")

    class Meta:
        verbose_name = "Строка поставки"
        verbose_name_plural = "Строки поставок"

    def __str__(self):
        return f"{self.arrival} | {self.item} {self.qty} {self.uom}"
