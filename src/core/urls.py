from decouple import config
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('store/', include('apps.store.urls')),
    path('cart/', include('apps.cart.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('orders/', include('apps.orders.urls')),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path(config('ADMIN_URL'), admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
