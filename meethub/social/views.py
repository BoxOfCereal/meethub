from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q

from meethub.accounts.models import Account
from .models import Friendship, Follow, Block


class SendFriendRequest(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        receiver = get_object_or_404(Account, pk=user_id)
        
        # Check if friendship already exists
        existing_friendship = Friendship.objects.filter(
            Q(requester=request.user, receiver=receiver) |
            Q(requester=receiver, receiver=request.user)
        ).first()
        
        if existing_friendship:
            if existing_friendship.status == 'pending':
                messages.warning(request, f'Friend request already pending with {receiver.get_fullname()}')
            elif existing_friendship.status == 'accepted':
                messages.info(request, f'You are already friends with {receiver.get_fullname()}')
            elif existing_friendship.status == 'rejected':
                messages.warning(request, f'Friend request was previously rejected by {receiver.get_fullname()}')
        elif receiver.profile.allow_friend_requests:
            Friendship.objects.create(requester=request.user, receiver=receiver)
            messages.success(request, f'Friend request sent to {receiver.get_fullname()}')
        else:
            messages.error(request, f'{receiver.get_fullname()} is not accepting friend requests')
        
        return redirect('profile:detail-map', pk=receiver.id)


class AcceptFriendRequest(LoginRequiredMixin, generic.View):
    def post(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, pk=friendship_id, receiver=request.user)
        friendship.status = 'accepted'
        friendship.save()
        messages.success(request, f'You are now friends with {friendship.requester.get_fullname()}')
        # Redirect to the requester's profile so you can see them as a friend
        return redirect('profile:detail-map', pk=friendship.requester.id)


class RejectFriendRequest(LoginRequiredMixin, generic.View):
    def post(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, pk=friendship_id, receiver=request.user)
        friendship.status = 'rejected'
        friendship.save()
        messages.success(request, f'Friend request from {friendship.requester.get_fullname()} rejected')
        # Redirect to your own profile to see updated pending requests
        return redirect('profile:detail-map', pk=request.user.id)


class Unfriend(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        other_user = get_object_or_404(Account, pk=user_id)
        Friendship.objects.filter(
            Q(requester=request.user, receiver=other_user) |
            Q(requester=other_user, receiver=request.user)
        ).delete()
        messages.success(request, f'You are no longer friends with {other_user.get_fullname()}')
        return redirect('profile:detail-map', pk=other_user.id)


class FollowUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        following = get_object_or_404(Account, pk=user_id)
        Follow.objects.get_or_create(follower=request.user, following=following)
        messages.success(request, f'You are now following {following.get_fullname()}')
        return redirect('profile:detail-map', pk=following.id)


class UnfollowUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        following = get_object_or_404(Account, pk=user_id)
        Follow.objects.filter(follower=request.user, following=following).delete()
        messages.success(request, f'You are no longer following {following.get_fullname()}')
        return redirect('profile:detail-map', pk=following.id)


class BlockUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        blocked = get_object_or_404(Account, pk=user_id)
        Block.objects.get_or_create(blocker=request.user, blocked=blocked)
        messages.success(request, f'You have blocked {blocked.get_fullname()}')
        return redirect('profile:detail-map', pk=blocked.id)


class UnblockUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        blocked = get_object_or_404(Account, pk=user_id)
        Block.objects.filter(blocker=request.user, blocked=blocked).delete()
        messages.success(request, f'You have unblocked {blocked.get_fullname()}')
        return redirect('profile:detail-map', pk=blocked.id)
