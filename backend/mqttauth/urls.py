from django.conf.urls import url

from . import views

app_name = 'mqttauth'
urlpatterns = [
    url(r'^auth/$', views.auth, name='auth'),
    url(r'^superuser/$', views.superuser, name='superuser'),
    url(r'^acl/$', views.acl, name='acl'),
]
