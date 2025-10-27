from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movement
from .services import apply_movement


# необязательно, но полезно: оценка порогов после пересчёта
def _evaluate_thresholds_for(inventories):
    try:
        from apps.thresholds.services import evaluate_thresholds
    except Exception:
        return
    for inv in inventories:
        try:
            evaluate_thresholds(inv)
        except Exception:
            pass


@receiver(post_save, sender=Movement)
def on_movement_created(sender, instance: Movement, created, **kwargs):
    # только при создании, чтобы не «дублировать» пересчёт
    if not created:
        return
    touched = apply_movement(instance)
    _evaluate_thresholds_for(touched)
