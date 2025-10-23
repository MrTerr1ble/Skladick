from django.db import models


class SyncQueue(models.Model):
    """Оффлайн-очередь синхронизации/интеграций."""
    PENDING, SENT, ACK, ERROR = "PENDING", "SENT", "ACK", "ERROR"
    STATE = [(PENDING, "В очереди"), (SENT, "Отправлено"), (ACK, "Подтверждено"), (ERROR, "Ошибка")]

    entity = models.CharField("Сущность", max_length=64)            # e.g. 'Movement', 'Inventory'
    operation = models.CharField("Операция", max_length=32)         # e.g. 'CREATE', 'UPDATE', 'DELETE'
    payload = models.JSONField("Данные")
    correlation_id = models.CharField("Корреляция", max_length=64, unique=True)
    state = models.CharField("Статус", max_length=8, choices=STATE, default=PENDING, db_index=True)
    retry_count = models.PositiveIntegerField("Попыток", default=0)
    last_error = models.TextField("Ошибка", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Очередь синхронизации"
        verbose_name_plural = "Очередь синхронизации"
        indexes = [models.Index(fields=["state", "created_at"])]

    def __str__(self):
        return f"{self.entity}:{self.operation} [{self.state}]"
