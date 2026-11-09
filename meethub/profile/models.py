from django.db import models
from django.conf import settings
from django.shortcuts import reverse

from meethub.events.models import Event
from meethub.accounts.models import Account
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)  # {'twitter': '', 'instagram': '', etc.}
    allow_friend_requests = models.BooleanField(default=True)
    allow_wall_posts = models.BooleanField(default=True)
    allow_non_friend_wall_comments = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'profiles'

    def __str__(self):
        return '{0}\'s profile'.format(self.user.first_name)

    def get_absolute_url(self):
        return reverse('profile:detail', kwargs={'pk': self.pk})

    def get_date_of_birth(self):
        return self.date_of_birth

    def is_attending(self):
        if Event.objects.filter(pk=self.pk, attendees=self.user).exists():
            return True
