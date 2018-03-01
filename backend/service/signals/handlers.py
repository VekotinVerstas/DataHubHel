from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Service, ServiceToken


@receiver(post_save, sender=Service)
def create_service_token(sender, instance=None, created=False, **kwargs):
    if created:
        ServiceToken.objects.create(service=instance)
