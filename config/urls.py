from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from book.views import OPACView   # ← import the view
from book.views import DashboardView, OPACView, TVAdsView, TurnstileGateView,BookDetailView
from library_service import views as library_views
from library_service.views import scanner_page


urlpatterns = [

    path("admin/", admin.site.urls),

    # Dashboard (keeps your simple TemplateView)
    path(
        "dashboard/",
        DashboardView.as_view(),
        name="dashboard",
    ),


    path("tv-ads/", TVAdsView.as_view(), name="tv_ads"),
    path("turnstile-gate/", TurnstileGateView.as_view(), name="turnstile_gate"),
    # OPAC — now uses the real view
    path("", OPACView.as_view(), name="opac"),
    path("opac/book/<int:pk>/", BookDetailView.as_view(), name="book_detail"), 
    path("api/scan/", library_views.scan_gate_api, name="scan_gate_api"),   
    path("scanner/", library_views.scanner_page, name="scanner"),   
    path("scanner/latest/", library_views.latest_scan, name="latest_scan"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)