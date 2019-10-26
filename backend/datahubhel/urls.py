from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import datahubhel.dhh_auth.urls
import datahubhel.gatekeeper.urls
import datahubhel.mqttauth.urls
import datahubhel.service.urls
import ta120_adapter.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(datahubhel.dhh_auth.urls)),
    path('api/', include(datahubhel.service.urls)),
    path('api/', include(datahubhel.gatekeeper.urls)),
    path('mqttauth/', include(datahubhel.mqttauth.urls)),
    path('cesva/v1/', include(ta120_adapter.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
