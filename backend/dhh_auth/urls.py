from django.urls import path

from . import api

urlpatterns = [
    path('me/', api.MeView.as_view(), name='personal-data'),
    path('me/register/', api.RegisterView.as_view(), name='register-user'),
    path('me/forget/', api.ForgetView.as_view(), name='forget-user'),
]
