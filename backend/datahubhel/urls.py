from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import dhh_auth.urls
import gatekeeper.urls
import mqttauth.urls
import service.urls
import ta120_adapter.urls
import datahubhel.sta.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(dhh_auth.urls)),
    path('api/', include(service.urls)),
    path('api/', include(datahubhel.sta.urls)),
    path('api/', include(gatekeeper.urls)),
    path('mqttauth/', include(mqttauth.urls)),
    path('ta120/', include(ta120_adapter.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
