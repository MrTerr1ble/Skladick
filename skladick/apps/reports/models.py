from django.db import models


class CalcLog(models.Model):
    """Журнал расчётов/отчётов (фоновые задачи)."""
    RUNNING, SUCCESS, FAILED = "RUNNING", "SUCCESS", "FAILED"
    STATUS = [(RUNNING, "Выполняется"), (SUCCESS, "Успешно"), (FAILED, "Ошибка")]

    calc_type = models.CharField("Тип расчёта/отчёта", max_length=64)   # e.g. 'inventory_summary'
    params = models.JSONField("Параметры", default=dict)
    started_at = models.DateTimeField("Начато", auto_now_add=True)
    finished_at = models.DateTimeField("Завершено", null=True, blank=True)
    status = models.CharField("Статус", max_length=8, choices=STATUS, default=RUNNING, db_index=True)
    rows_read = models.BigIntegerField("Строк прочитано", default=0)
    rows_written = models.BigIntegerField("Строк записано", default=0)
    result_ref = models.CharField("Результат (ссылка/путь)", max_length=255, blank=True)
    error_message = models.TextField("Ошибка", blank=True)

    class Meta:
        verbose_name = "Журнал расчёта"
        verbose_name_plural = "Журналы расчётов"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.calc_type} [{self.status}]"
