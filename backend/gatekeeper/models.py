from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class EntityBase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    sts_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class Thing(EntityBase):
    class Meta:
        verbose_name = 'thing'
        verbose_name_plural = 'things'


class Datastream(EntityBase):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'data stream'
        verbose_name_plural = 'data streams'
        permissions = (
            ('subscribe_datastream', 'Can subscribe to the data stream topic'),
            ('publish_datastream', 'Can publish to the data stream topic'),
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
