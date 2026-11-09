from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models

from meethub.events.models import Event
from meethub.comments.models import Comment
from meethub.accounts.models import Account
from meethub.profile.forms import ProfileForm, UserForm
from meethub.profile.models import Profile


# Create your views here.

@login_required()
def edit_profile(request):

    # This line is a part of the connection to Cloudinary API
    context = dict(backend_form=ProfileForm())

    if request.method == 'POST':
        user_form = UserForm(instance=request.user, data=request.POST)
        profile_form = ProfileForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        context['posted'] = profile_form.instance

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

    else:

        # This creates a profile for users that don't have a profile.
        # They didn't have a profile because they registered before the profile feature was added.
        # A profile is created for a user during the process of signup.

        Profile.objects.get_or_create(user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'profile/update_form.html', {'user_form': user_form, 'profile_form': profile_form})


class UserDetail(LoginRequiredMixin, generic.DetailView):
    model = Account
    template_name = 'profile/profile_detail.html'
    context_object_name = 'account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.get_object()
        context['events'] = Event.objects.filter(creator=account)
        context['comments'] = Comment.objects.filter(created_by=account)
        
        # Add friendship status
        from meethub.social.models import Friendship, Follow, Block
        if account != self.request.user:
            friendship = Friendship.objects.filter(
                models.Q(requester=self.request.user, receiver=account) |
                models.Q(requester=account, receiver=self.request.user)
            ).first()
            context['friendship'] = friendship
            context['is_following'] = Follow.objects.filter(
                follower=self.request.user, following=account
            ).exists()
            context['is_blocked'] = Block.objects.filter(
                blocker=self.request.user, blocked=account
            ).exists()
        else:
            # Show pending friend requests for own profile
            context['pending_friend_requests'] = Friendship.objects.filter(
                receiver=self.request.user, status='pending'
            )
            # Show accepted friends for own profile
            context['friends'] = Friendship.objects.filter(
                models.Q(requester=self.request.user) | models.Q(receiver=self.request.user),
                status='accepted'
            )
        
        return context


class UserDetailMap(LoginRequiredMixin, generic.DetailView):
    model = Account
    template_name = 'profile/profile_map.html'
    context_object_name = 'account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.get_object()
        context['events'] = Event.objects.filter(creator=account)
        context['comments'] = Comment.objects.filter(created_by=account)
        
        # Add friendship status
        from meethub.social.models import Friendship, Follow, Block
        if account != self.request.user:
            friendship = Friendship.objects.filter(
                models.Q(requester=self.request.user, receiver=account) |
                models.Q(requester=account, receiver=self.request.user)
            ).first()
            context['friendship'] = friendship
            context['is_following'] = Follow.objects.filter(
                follower=self.request.user, following=account
            ).exists()
            context['is_blocked'] = Block.objects.filter(
                blocker=self.request.user, blocked=account
            ).exists()
        else:
            # Show pending friend requests for own profile
            context['pending_friend_requests'] = Friendship.objects.filter(
                receiver=self.request.user, status='pending'
            )
            # Show accepted friends for own profile
            context['friends'] = Friendship.objects.filter(
                models.Q(requester=self.request.user) | models.Q(receiver=self.request.user),
                status='accepted'
            )
        
        return context
