from django.urls import path
from rest_framework import routers

from . import api

router = routers.SimpleRouter()

router.register('user-tokens', api.TokenViewSet, base_name='user-token')

urlpatterns = router.urls + [
    path('me/', api.MeView.as_view(), name='personal-data'),
    path('me/register/', api.RegisterView.as_view(), name='register-user'),
    path('me/forget/', api.ForgetView.as_view(), name='forget-user'),
]
