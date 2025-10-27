from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='procurement:purchase_request_list', permanent=False)),
    path('procurement/', include('apps.procurement.urls')),
]
