from django.conf.urls import url

from . import views

app_name = 'gatekeeper'
urlpatterns = [
    url(r'^(?P<path>.*)$', views.index, name='index'),
]
