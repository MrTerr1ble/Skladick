from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- стандартные страницы авторизации/регистрации Django ---
    path("accounts/", include("django.contrib.auth.urls")),

    # --- твои приложения ---
    path("ore/", include(("apps.ore.urls", "ore"), namespace="ore")),
    path("inventory/", include(("apps.inventory.urls", "inventory"), namespace="inventory")),
    path("thresholds/", include(("apps.thresholds.urls", "thresholds"), namespace="thresholds")),
    path("procurement/", include(("apps.procurement.urls", "procurement"), namespace="procurement")),

    path("", RedirectView.as_view(pattern_name="ore:receipt_list", permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=getattr(settings, "STATIC_ROOT", None))
