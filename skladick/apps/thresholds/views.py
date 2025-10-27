from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from .models import Alert


class AlertListView(ListView):
    model = Alert
    template_name = "thresholds/alert_list.html"
    context_object_name = "alerts"
    paginate_by = 50
    ordering = "-created_at"


@login_required
def alert_action(request, pk, action):
    alert = get_object_or_404(Alert, pk=pk)
    if request.method == "POST":
        if action == "ack" and alert.state == "OPEN":
            alert.state = "ACK"
        elif action == "close" and alert.state in ("OPEN","ACK"):
            alert.state = "CLOSED"
        alert.save(update_fields=["state"])
    return redirect("thresholds:alert_list")
