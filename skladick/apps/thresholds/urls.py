from django.urls import path
from .views import AlertListView, alert_action, alerts_api

app_name = "thresholds"

urlpatterns = [
    path("alerts/", AlertListView.as_view(), name="alert_list"),
    path("alerts/<int:pk>/<str:action>/", alert_action, name="alert_action"),
    path("alerts/api/", alerts_api, name="alerts_api"),
]
