from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Permission, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dhh_auth.utils import get_perm_obj
from utils.models import TimestampedUUIDModel


class ClientPermission(TimestampedUUIDModel):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    client = models.ForeignKey('Client', related_name='clientpermission', on_delete=models.CASCADE)
    permitted_by = models.ForeignKey('User', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.CharField(_('object ID'), max_length=255)
    content_object = GenericForeignKey(fk_field='object_pk')

    class Meta:
        unique_together = ['client', 'permission', 'content_type', 'object_pk']


class Client(TimestampedUUIDModel):

    def _get_perms(self, permission, objects, object_lookup_field):
        # TODO: Add caching
        if isinstance(objects, QuerySet):
            objects = list(objects)

        if not isinstance(objects, list):
            objects = [objects]
        return (
            ClientPermission.objects
                .filter(permission=permission,
                        client=self,
                        content_type=permission.content_type,
                        object_pk__in=[getattr(obj, object_lookup_field) for obj in objects])
        )

    def has_obj_perm(self, perm, obj, object_lookup_field='sts_id'):
        permission = get_perm_obj(perm, obj)
        obj_permission = self._get_perms(permission, obj, object_lookup_field)

        if not obj_permission:
            return False
        return True

    def has_any_obj_perm(self, perm, objects, object_lookup_field='sts_id'):
        permission = get_perm_obj(perm, objects[0])
        obj_permissions = self._get_perms(permission, objects, object_lookup_field)

        if not obj_permissions:
            return False
        return True

    def has_all_obj_perm(self, perm, objects, object_lookup_field='sts_id'):
        permission = get_perm_obj(perm, objects[0])
        obj_permissions = self._get_perms(permission, objects, object_lookup_field)

        if not obj_permissions or len(obj_permissions) != len(objects):
            return False
        return True

    def create_perm(self, perm, obj, permitted_by):
        permission = get_perm_obj(perm, obj)
        return ClientPermission.objects.create(
            client=self,
            permission=permission,
            content_type=permission.content_type,
            object_pk=obj.id,
            permitted_by=permitted_by,
        )

    def __str__(self):
        return str(self.id)


class AbstractClientUser(AbstractBaseUser, TimestampedUUIDModel):
    """
    User to model that stores additional client informatin

    The purpose of the model is to have an additional client instance
    linked to
    """
    client = models.OneToOneField(Client, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not getattr(self, 'client', None):
            self.client = Client.objects.create()
        super().save(*args, **kwargs)

    def get_full_name(self):
        raise NotImplementedError('subclasses of AbstractClientUser must provide a get_full_name() method')

    def get_short_name(self):
        raise NotImplementedError('subclasses of AbstractClientUser must provide a get_short_name() method.')

    class Meta:
        abstract = True


class User(AbstractClientUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super(AbstractClientUser, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
