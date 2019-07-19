from django.conf.urls import url

from .endpoint import Endpoint

app_name = 'ta120_adapter'
urlpatterns = [
    url(r'^', Endpoint.as_view()),
]
