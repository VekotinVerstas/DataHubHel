import binascii
import os

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from datahubhel.dhh_auth.models import AbstractClientUser


class Service(AbstractClientUser):
    maintainers = models.ManyToManyField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    identifier_validator = UnicodeUsernameValidator()
    identifier = models.CharField(
        _('identifier'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[identifier_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    # Django 2.0 requires an email field
    # The field is only used when authentication for (in 2.0)
    # and since we are currently not going to use the django forms
    # at all this is a solution for now.
    EMAIL_FIELD = 'identifier'
    USERNAME_FIELD = 'identifier'

    def get_full_name(self):
        return '[{}] {}'.format(self.identifier, self.name)

    def get_short_name(self):
        return self.identifier

    class Meta:
        permissions = (
            ('administrate_service', 'Can administrate a service'),
        )

    def __str__(self):
        return self.name if self.name else self.id

    def save(self, *args, **kwargs):
        # Make sure that we never have a
        # usable password for services.
        if self.has_usable_password():
            self.set_unusable_password()
        super().save(*args, **kwargs)


class ServiceToken(TimeStampedModel):
    service = models.ForeignKey(Service, related_name='keys', on_delete=models.CASCADE)
    key = models.CharField(max_length=255)

    def save(self, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ServiceToken, self).save(**kwargs)

    def renew_key(self):
        self.key = self.generate_key()
        self.save()

    def generate_key(self):
        return binascii.hexlify(os.urandom(32)).decode()

    def __str__(self):
        return self.service.identifier
