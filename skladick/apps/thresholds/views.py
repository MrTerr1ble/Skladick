from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView
from django.http import JsonResponse
from .models import Alert


class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = "thresholds/alert_list.html"
    context_object_name = "alerts"
    paginate_by = 50
    ordering = "-created_at"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        if "page" in query:
            query.pop("page")
        ctx["querystring"] = query.urlencode()
        return ctx


@login_required
def alert_action(request, pk, action):
    alert = get_object_or_404(Alert, pk=pk)
    if request.method == "POST":
        now = timezone.now()
        if action == "ack" and alert.state == Alert.OPEN:
            alert.state = Alert.ACK
            alert.acknowledged_at = now
            alert.save(update_fields=["state", "acknowledged_at"])
        elif action == "close" and alert.state in (Alert.OPEN, Alert.ACK):
            alert.state = Alert.CLOSED
            if alert.acknowledged_at is None:
                alert.acknowledged_at = now
            alert.closed_at = now
            alert.save(update_fields=["state", "acknowledged_at", "closed_at"])
    return redirect("thresholds:alert_list")


@login_required
def alerts_api(request):
    """Возвращает последние открытые алерты для уведомлений."""
    alerts = (
        Alert.objects.filter(state=Alert.OPEN)
        .select_related("item", "uom", "warehouse", "location")
        .order_by("-created_at")[:5]
    )
    data = [
        {
            "id": alert.id,
            "item": alert.item.name,
            "current_qty": str(alert.current_qty),
            "uom": alert.uom.code,
            "warehouse": alert.warehouse.name,
            "location": alert.location.code if alert.location else "—",
            "message": alert.message or "",
            "severity": alert.get_severity_display(),
            "severity_code": alert.severity,
        }
        for alert in alerts
    ]
    return JsonResponse(data, safe=False)
