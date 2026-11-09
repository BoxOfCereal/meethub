from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from meethub.accounts.managers import AccountManager

# Create your models here.


class Account(AbstractBaseUser, PermissionsMixin):
    is_client = models.BooleanField('client status', default=False)

    first_name = models.CharField(_('first name'), max_length=200)
    last_name = models.CharField(_('last name'), max_length=200)
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into the admin site.'),
    )

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'is_client']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_fullname()

    def clean(self):
        super().clean()

    def get_first_name(self):
        """
        Return the first name
        """
        return self.first_name

    def get_fullname(self):
        """
        Return the fullname
        :return: fullname
        """
        fullname = '{} {}'.format(self.last_name, self.first_name)
        return fullname

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this user
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
        return True

    def get_friends(self):
        """Get accepted friends"""
        from meethub.social.models import Friendship
        friend_ids = Friendship.objects.filter(
            models.Q(requester=self) | models.Q(receiver=self),
            status='accepted'
        ).values_list('requester', 'receiver')
        friend_ids = set([fid for pair in friend_ids for fid in pair])
        friend_ids.discard(self.id)
        return Account.objects.filter(id__in=friend_ids)

    def get_friends_of_friends(self):
        """Get friends of friends"""
        friends = self.get_friends()
        fof_ids = set()
        for friend in friends:
            fof_ids.update(friend.get_friends().values_list('id', flat=True))
        fof_ids.discard(self.id)
        fof_ids.difference_update(self.get_friends().values_list('id', flat=True))
        return Account.objects.filter(id__in=fof_ids)

    def is_blocked_by(self, user):
        """Check if user blocked this account"""
        from meethub.social.models import Block
        return Block.objects.filter(blocker=user, blocked=self).exists()

    def has_blocked(self, user):
        """Check if this account blocked user"""
        from meethub.social.models import Block
        return Block.objects.filter(blocker=self, blocked=user).exists()

    def can_view_event(self, event):
        """Check if user can view private event"""
        return event.can_view(self)

    def can_post_on_wall(self, wall_owner):
        """Check if user can post on someone's wall"""
        if not wall_owner.profile.allow_wall_posts:
            return False
        if wall_owner == self:
            return True
        if self in wall_owner.get_friends():
            return True
        return False
