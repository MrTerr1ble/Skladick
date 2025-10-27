from django.urls import path
from .views import AlertListView, alert_action

app_name = "thresholds"

urlpatterns = [
    path("alerts/", AlertListView.as_view(), name="alert_list"),
    path("alerts/<int:pk>/<str:action>/", alert_action, name="alert_action"),
]
