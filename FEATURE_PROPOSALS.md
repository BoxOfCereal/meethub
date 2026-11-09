# Feature Proposals for MeetHub

This document contains two major feature proposals for the MeetHub platform. Each proposal is self-contained and can be implemented independently.

---

# Feature Proposal 1: Social Networking System

## Overview
Implement a comprehensive social networking system including friend/follow relationships, user walls, private events, moderation tools, and comment reply chains.

## 1. New Models to Create

### A. Relationship Models (Create `social` app)

#### Friendship Model
```python
# social/models.py
from django.db import models
from meethub.accounts.models import Account

class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    requester = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['requester', 'receiver']
    
    def is_accepted(self):
        return self.status == 'accepted'
    
    def __str__(self):
        return f"{self.requester} -> {self.receiver} ({self.status})"
```

#### Follow Model
```python
class Follow(models.Model):
    follower = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
    
    def __str__(self):
        return f"{self.follower} follows {self.following}"
```

#### Block Model
```python
class Block(models.Model):
    blocker = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blocker', 'blocked']
    
    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"
```

### B. User Wall Models (in `social` app)

#### WallPost Model
```python
class WallPost(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='wall_posts')
    wall_owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='posts_on_wall')
    content = models.TextField(max_length=2000)
    image = models.ImageField(upload_to='wall_posts/', blank=True, null=True)
    links = models.JSONField(default=list, blank=True)  # Store links as array
    allow_non_friend_comments = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.author} on {self.wall_owner}'s wall"
```

#### WallComment Model
```python
class WallComment(models.Model):
    post = models.ForeignKey(WallPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author}"
    
    def get_replies(self):
        return self.replies.all()
```

### C. Moderation Models (Create `moderation` app)

#### Report Model
```python
# moderation/models.py
from django.db import models
from meethub.accounts.models import Account

class Report(models.Model):
    REPORT_TYPES = [
        ('user', 'User'),
        ('event', 'Event'),
        ('wall_post', 'Wall Post'),
        ('comment', 'Comment'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    reporter = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='reports_received')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    content_id = models.PositiveIntegerField()  # ID of reported object
    reason = models.TextField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    action_taken = models.CharField(max_length=100, blank=True)
    escalation_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Report on {self.reported_user} ({self.report_type})"
```

#### Ban Model
```python
class Ban(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='bans')
    banned_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='bans_issued')
    reason = models.TextField(max_length=500)
    is_permanent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Ban on {self.user} ({'permanent' if self.is_permanent else 'temporary'})"
    
    def is_expired(self):
        if self.is_permanent:
            return False
        return timezone.now() > self.expires_at if self.expires_at else False
```

### D. Event Privacy Enhancements

Add to existing `Event` model in `events/models.py`:

```python
class Event(models.Model):
    # ... existing fields ...
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('friends_of_friends', 'Friends of Friends'),
        ('invite_only', 'Invite Only'),
    ]
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    invited_users = models.ManyToManyField(Account, related_name='invited_events', blank=True)
    
    def can_view(self, user):
        """Check if user can view this event based on privacy"""
        if self.privacy_level == 'public':
            return True
        if self.privacy_level == 'invite_only':
            return self.invited_users.filter(id=user.id).exists() or self.creator == user
        if self.privacy_level == 'friends':
            return user in self.creator.get_friends() or self.creator == user
        if self.privacy_level == 'friends_of_friends':
            friends = self.creator.get_friends()
            fof = self.creator.get_friends_of_friends()
            return user in friends or user in fof or self.creator == user
        return False
```

## 2. Account Model Enhancements

### Add to Profile Model (`profile/models.py`)

```python
class Profile(models.Model):
    # ... existing fields ...
    
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)  # {'twitter': '', 'instagram': '', etc.}
    allow_friend_requests = models.BooleanField(default=True)
    allow_wall_posts = models.BooleanField(default=True)
    allow_non_friend_wall_comments = models.BooleanField(default=False)
```

### Add Helper Methods to Account Model (`accounts/models.py`)

```python
from django.db import models
from meethub.social.models import Friendship, Block

class Account(AbstractBaseUser, PermissionsMixin):
    # ... existing fields and methods ...
    
    def get_friends(self):
        """Get accepted friends"""
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
        return Block.objects.filter(blocker=user, blocked=self).exists()
    
    def has_blocked(self, user):
        """Check if this account blocked user"""
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
```

## 3. Views to Create

### Social App Views

```python
# social/views.py
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q

from meethub.accounts.models import Account
from meethub.social.models import Friendship, Follow, Block, WallPost, WallComment

class SendFriendRequest(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        receiver = get_object_or_404(Account, pk=user_id)
        if receiver.profile.allow_friend_requests:
            Friendship.objects.create(requester=request.user, receiver=receiver)
            messages.success(request, f'Friend request sent to {receiver.get_fullname()}')
        else:
            messages.error(request, f'{receiver.get_fullname()} is not accepting friend requests')
        return redirect('profile:detail', pk=receiver.profile.pk)

class AcceptFriendRequest(LoginRequiredMixin, generic.View):
    def post(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, pk=friendship_id, receiver=request.user)
        friendship.status = 'accepted'
        friendship.save()
        messages.success(request, f'You are now friends with {friendship.requester.get_fullname()}')
        return redirect('profile:detail', pk=request.user.profile.pk)

class RejectFriendRequest(LoginRequiredMixin, generic.View):
    def post(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, pk=friendship_id, receiver=request.user)
        friendship.status = 'rejected'
        friendship.save()
        messages.success(request, f'Friend request from {friendship.requester.get_fullname()} rejected')
        return redirect('profile:detail', pk=request.user.profile.pk)

class Unfriend(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        other_user = get_object_or_404(Account, pk=user_id)
        Friendship.objects.filter(
            Q(requester=request.user, receiver=other_user) |
            Q(requester=other_user, receiver=request.user)
        ).delete()
        messages.success(request, f'You are no longer friends with {other_user.get_fullname()}')
        return redirect('profile:detail', pk=other_user.profile.pk)

class FollowUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        following = get_object_or_404(Account, pk=user_id)
        Follow.objects.get_or_create(follower=request.user, following=following)
        messages.success(request, f'You are now following {following.get_fullname()}')
        return redirect('profile:detail', pk=following.profile.pk)

class UnfollowUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        following = get_object_or_404(Account, pk=user_id)
        Follow.objects.filter(follower=request.user, following=following).delete()
        messages.success(request, f'You are no longer following {following.get_fullname()}')
        return redirect('profile:detail', pk=following.profile.pk)

class BlockUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        blocked = get_object_or_404(Account, pk=user_id)
        Block.objects.get_or_create(blocker=request.user, blocked=blocked)
        messages.success(request, f'You have blocked {blocked.get_fullname()}')
        return redirect('profile:detail', pk=blocked.profile.pk)

class UnblockUser(LoginRequiredMixin, generic.View):
    def post(self, request, user_id):
        blocked = get_object_or_404(Account, pk=user_id)
        Block.objects.filter(blocker=request.user, blocked=blocked).delete()
        messages.success(request, f'You have unblocked {blocked.get_fullname()}')
        return redirect('profile:detail', pk=blocked.profile.pk)

class CreateWallPost(LoginRequiredMixin, generic.CreateView):
    model = WallPost
    template_name = 'social/create_wall_post.html'
    fields = ['content', 'image', 'links', 'allow_non_friend_comments']
    
    def form_valid(self, form):
        wall_owner = get_object_or_404(Account, pk=self.kwargs['user_id'])
        if not self.request.user.can_post_on_wall(wall_owner):
            messages.error(self.request, 'You cannot post on this wall')
            return redirect('profile:detail', pk=wall_owner.profile.pk)
        form.instance.author = self.request.user
        form.instance.wall_owner = wall_owner
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('profile:detail', kwargs={'pk': self.object.wall_owner.profile.pk})

class WallPostDetail(LoginRequiredMixin, generic.DetailView):
    model = WallPost
    template_name = 'social/wall_post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(parent=None)
        return context
```

### Moderation App Views

```python
# moderation/views.py
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from meethub.accounts.models import Account
from meethub.moderation.models import Report, Ban

class CreateReport(LoginRequiredMixin, generic.CreateView):
    model = Report
    template_name = 'moderation/create_report.html'
    fields = ['report_type', 'content_id', 'reason']
    
    def form_valid(self, form):
        reported_user = get_object_or_404(Account, pk=self.kwargs['user_id'])
        form.instance.reporter = self.request.user
        form.instance.reported_user = reported_user
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Your report has been submitted')
        return reverse_lazy('profile:detail', kwargs={'pk': self.kwargs['profile_pk']})
```

## 4. URL Patterns

### Social App URLs

```python
# social/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('friend-request/send/<int:user_id>/', views.SendFriendRequest.as_view(), name='send-friend-request'),
    path('friend-request/accept/<int:friendship_id>/', views.AcceptFriendRequest.as_view(), name='accept-friend-request'),
    path('friend-request/reject/<int:friendship_id>/', views.RejectFriendRequest.as_view(), name='reject-friend-request'),
    path('unfriend/<int:user_id>/', views.Unfriend.as_view(), name='unfriend'),
    path('follow/<int:user_id>/', views.FollowUser.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', views.UnfollowUser.as_view(), name='unfollow-user'),
    path('block/<int:user_id>/', views.BlockUser.as_view(), name='block-user'),
    path('unblock/<int:user_id>/', views.UnblockUser.as_view(), name='unblock-user'),
    path('wall/post/create/<int:user_id>/', views.CreateWallPost.as_view(), name='create-wall-post'),
    path('wall/post/<int:pk>/', views.WallPostDetail.as_view(), name='wall-post-detail'),
]
```

### Moderation App URLs

```python
# moderation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('report/create/<int:user_id>/<int:profile_pk>/', views.CreateReport.as_view(), name='create-report'),
]
```

## 5. Forms

### Social App Forms

```python
# social/forms.py
from django import forms
from meethub.social.models import Friendship, Follow, Block

class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = Friendship
        fields = []  # No fields needed, created via view

class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = []  # No fields needed, created via view

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = []  # No fields needed, created via view
```

### Moderation App Forms

```python
# moderation/forms.py
from django import forms
from meethub.moderation.models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'content_id', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
```

## 6. Admin Registration

```python
# social/admin.py
from django.contrib import admin
from .models import Friendship, Follow, Block, WallPost, WallComment

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['requester', 'receiver', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['requester__username', 'receiver__username']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    search_fields = ['follower__username', 'following__username']

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
    search_fields = ['blocker__username', 'blocked__username']

@admin.register(WallPost)
class WallPostAdmin(admin.ModelAdmin):
    list_display = ['author', 'wall_owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'wall_owner__username', 'content']

@admin.register(WallComment)
class WallCommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'content']
```

```python
# moderation/admin.py
from django.contrib import admin
from .models import Report, Ban

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported_user', 'report_type', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'report_type', 'created_at']
    search_fields = ['reporter__username', 'reported_user__username', 'reason']

@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ['user', 'banned_by', 'is_permanent', 'expires_at', 'is_active', 'created_at']
    list_filter = ['is_permanent', 'is_active', 'created_at']
    search_fields = ['user__username', 'banned_by__username', 'reason']
```

## 7. Signal Handling

```python
# social/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Friendship

@receiver(post_save, sender=Friendship)
def friendship_accepted_notification(sender, instance, created, **kwargs):
    """Send notification when friendship is accepted"""
    if not created and instance.status == 'accepted':
        # Create notification for both users
        from meethub.notifications.models import Notification
        Notification.objects.create(
            user=instance.requester,
            message=f"{instance.receiver.get_fullname()} accepted your friend request!",
            notification_type='friendship_accepted'
        )
        Notification.objects.create(
            user=instance.receiver,
            message=f"You are now friends with {instance.requester.get_fullname()}!",
            notification_type='friendship_accepted'
        )
```

```python
# social/apps.py
from django.apps import AppConfig

class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meethub.social'

    def ready(self):
        import meethub.social.signals
```

## 8. Validation Improvements

```python
# social/models.py - Add validation to prevent self-relationships
from django.core.exceptions import ValidationError

class Friendship(models.Model):
    # ... existing fields ...

    def clean(self):
        if self.requester == self.receiver:
            raise ValidationError("Cannot send friend request to yourself")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Follow(models.Model):
    # ... existing fields ...

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Cannot follow yourself")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Block(models.Model):
    # ... existing fields ...

    def clean(self):
        if self.blocker == self.blocked:
            raise ValidationError("Cannot block yourself")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

## 9. Tests

```python
# social/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Friendship, Follow, Block

class FriendshipModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')

    def test_friendship_creation(self):
        friendship = Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2
        )
        self.assertEqual(friendship.status, 'pending')

    def test_cannot_friend_self(self):
        with self.assertRaises(ValidationError):
            friendship = Friendship(
                requester=self.user1,
                receiver=self.user1
            )
            friendship.full_clean()

class FollowModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')

    def test_follow_creation(self):
        follow = Follow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        self.assertEqual(follow.follower, self.user1)

    def test_cannot_follow_self(self):
        with self.assertRaises(ValidationError):
            follow = Follow(
                follower=self.user1,
                following=self.user1
            )
            follow.full_clean()
```

## 10. Comment Reply Chain Implementation

The `Comment` model already has a `parent` field for reply chains. You need to:

### Update Event Detail Views

```python
# events/views.py - Update EventDisplay and EventDisplayMap
class EventDisplay(generic.DetailView):
    # ... existing code ...
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.filter(parent=None)  # Only top-level comments
        context['attending'] = self.get_object().attendees.all
        return context
```

### Create Reply Views

```python
# comments/views.py
class CommentReply(SuccessMessageMixin, generic.CreateView):
    model = Comment
    template_name = 'events/detail.html'
    fields = ('comment',)
    success_message = 'Reply was added successfully'
    
    def form_valid(self, form):
        parent_comment = get_object_or_404(Comment, pk=self.kwargs['comment_pk'])
        event = parent_comment.event
        form.instance = form.save(commit=False)
        form.instance.event = event
        form.instance.created_by = self.request.user
        form.instance.parent = parent_comment
        form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'pk': self.kwargs['event_pk']})
```

### Template Implementation

Create recursive template for comment replies:

```django
<!-- events/templates/events/comment_tree.html -->
{% load comments_tags %}
<div class="comment" data-comment-id="{{ comment.id }}">
    <div class="comment-header">
        <strong>{{ comment.created_by.get_fullname }}</strong>
        <small>{{ comment.created_date }} {{ comment.created_time }}</small>
    </div>
    <div class="comment-body">
        {{ comment.comment }}
    </div>
    <div class="comment-actions">
        <a href="{% url 'comments:reply' comment_pk=comment.id event_pk=comment.event.id %}">Reply</a>
    </div>
    {% if comment.get_children %}
        <div class="comment-replies">
            {% for reply in comment.get_children %}
                {% include 'events/comment_tree.html' with comment=reply %}
            {% endfor %}
        </div>
    {% endif %}
</div>
```

## 6. Implementation Priority

### Phase 1: Core Relationships
- [ ] Create `social` app
- [ ] Create Friendship, Follow, Block models
- [ ] Add helper methods to Account model
- [ ] Create views/forms for friend/follow/block actions
- [ ] Add URL patterns
- [ ] Update profile templates with friend/follow/block buttons

### Phase 2: User Walls
- [ ] Extend Profile model with bio, links, settings
- [ ] Create WallPost and WallComment models
- [ ] Build wall views and templates
- [ ] Add wall post creation form
- [ ] Implement wall comment system

### Phase 3: Event Privacy
- [ ] Add privacy_level and invited_users to Event model
- [ ] Update event views to check permissions
- [ ] Add invitation system
- [ ] Update event forms to include privacy settings
- [ ] Filter event lists based on privacy

### Phase 4: Moderation
- [ ] Create `moderation` app
- [ ] Create Report and Ban models
- [ ] Build report submission forms
- [ ] Add report buttons throughout the app
- [ ] Implement ban checking in views

### Phase 5: Comment Replies
- [ ] Implement reply chain UI in event comments
- [ ] Implement reply chain UI in wall comments
- [ ] Create recursive comment templates
- [ ] Add reply views and forms

---

# Feature Proposal 2: Admin Dashboard System

## Overview
Implement an administrative dashboard for reviewing reports, managing users, handling bans, and performing other administrative tasks. Includes admin user roles and comprehensive admin action logging.

## 1. Account Model Enhancement

Add admin field to `Account` model in `accounts/models.py`:

```python
class Account(AbstractBaseUser, PermissionsMixin):
    # ... existing fields ...
    
    is_admin = models.BooleanField(
        _('admin status'),
        default=False,
        help_text=_('Designates whether the user can access the admin dashboard.')
    )
    
    @property
    def is_admin_user(self):
        """Check if user has admin privileges"""
        return self.is_admin or self.is_staff or self.is_superuser
```

## 2. Create Admin Dashboard App

### App Structure
```
admin_dashboard/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
└── templates/
    └── admin_dashboard/
        ├── base.html
        ├── dashboard_home.html
        ├── report_list.html
        ├── report_detail.html
        ├── user_list.html
        ├── user_detail.html
        └── partials/
            ├── stats_cards.html
            └── activity_feed.html
```

## 3. Admin Mixin for Access Control

```python
# admin_dashboard/mixins.py
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is an admin."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_user:
            return redirect('login')  # Or custom permission denied page
        return super().dispatch(request, *args, **kwargs)
```

## 4. Enhanced Report Model

Update the Report model from Feature Proposal 1 with admin-specific fields:

```python
# moderation/models.py - Update Report model
class Report(models.Model):
    # ... existing fields from Feature Proposal 1 ...
    
    # Admin-specific fields (if not already added in Feature Proposal 1)
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    admin_notes = models.TextField(blank=True)
    action_taken = models.CharField(max_length=100, blank=True)  # 'user_banned', 'content_removed', etc.
    escalation_count = models.PositiveIntegerField(default=0)
    
    def escalate(self):
        """Escalate report priority"""
        priorities = ['low', 'medium', 'high', 'urgent']
        current_index = priorities.index(self.priority)
        if current_index < len(priorities) - 1:
            self.priority = priorities[current_index + 1]
            self.escalation_count += 1
            self.save()
```

## 5. Admin Action Logging Model

```python
# admin_dashboard/models.py
from django.db import models
from django.contrib.contenttypes.models import ContentType
from meethub.accounts.models import Account

class AdminActionLog(models.Model):
    ACTION_TYPES = [
        ('ban', 'Ban User'),
        ('unban', 'Unban User'),
        ('report_resolved', 'Report Resolved'),
        ('report_dismissed', 'Report Dismissed'),
        ('content_removed', 'Content Removed'),
        ('user_warned', 'User Warned'),
        ('user_muted', 'User Muted'),
        ('priority_changed', 'Priority Changed'),
    ]
    admin = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    target_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='admin_actions_received', null=True, blank=True)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.admin} - {self.action_type} - {self.timestamp}"
```

## 6. Admin Dashboard Views

### Dashboard Home

```python
# admin_dashboard/views.py
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .mixins import AdminRequiredMixin
from meethub.accounts.models import Account
from meethub.moderation.models import Report, Ban
from .models import AdminActionLog

class DashboardHome(AdminRequiredMixin, generic.TemplateView):
    template_name = 'admin_dashboard/dashboard_home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        thirty_days_ago = timezone.now() - timedelta(days=30)
        context['total_users'] = Account.objects.count()
        context['active_users'] = Account.objects.filter(date_joined__gte=thirty_days_ago).count()
        context['pending_reports'] = Report.objects.filter(status='pending').count()
        context['active_bans'] = Ban.objects.filter(is_active=True).count()
        
        # Reports resolved this week
        week_ago = timezone.now() - timedelta(days=7)
        context['reports_resolved_week'] = Report.objects.filter(
            status='resolved',
            reviewed_at__gte=week_ago
        ).count()
        
        # Recent activity
        context['recent_actions'] = AdminActionLog.objects.select_related('admin')[:10]
        context['recent_reports'] = Report.objects.select_related('reporter', 'reported_user')[:5]
        
        # Report type breakdown
        context['report_types'] = Report.objects.values('report_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return context
```

### Report Management Views

```python
class ReportListView(AdminRequiredMixin, generic.ListView):
    model = Report
    template_name = 'admin_dashboard/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Report.objects.select_related('reporter', 'reported_user', 'reviewed_by')
        
        # Filters
        status = self.request.GET.get('status')
        report_type = self.request.GET.get('type')
        priority = self.request.GET.get('priority')
        
        if status:
            queryset = queryset.filter(status=status)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')

class ReportDetailView(AdminRequiredMixin, generic.DetailView):
    model = Report
    template_name = 'admin_dashboard/report_detail.html'
    context_object_name = 'report'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.get_object()
        
        # Get reported content based on type
        if report.report_type == 'user':
            context['reported_content'] = Account.objects.get(pk=report.content_id)
        elif report.report_type == 'event':
            from meethub.events.models import Event
            context['reported_content'] = Event.objects.get(pk=report.content_id)
        elif report.report_type == 'wall_post':
            from meethub.social.models import WallPost
            context['reported_content'] = WallPost.objects.get(pk=report.content_id)
        elif report.report_type == 'comment':
            from meethub.comments.models import Comment
            context['reported_content'] = Comment.objects.get(pk=report.content_id)
        
        # User's report history
        context['user_report_history'] = Report.objects.filter(
            reported_user=report.reported_user
        ).exclude(pk=report.pk)[:5]
        
        return context

class ReportActionView(AdminRequiredMixin, generic.View):
    def post(self, request, report_id):
        report = get_object_or_404(Report, pk=report_id)
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'resolve':
            report.status = 'resolved'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.admin_notes = notes
            report.save()
            
            AdminActionLog.objects.create(
                admin=request.user,
                action_type='report_resolved',
                target_user=report.reported_user,
                reason=notes,
 details={'report_id': report.id}
            )
            messages.success(request, 'Report resolved')
            
        elif action == 'dismiss':
            report.status = 'dismissed'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.admin_notes = notes
            report.save()
            
            AdminActionLog.objects.create(
                admin=request.user,
                action_type='report_dismissed',
                target_user=report.reported_user,
                reason=notes,
                details={'report_id': report.id}
            )
            messages.success(request, 'Report dismissed')
            
        elif action == 'escalate':
            report.escalate()
            messages.success(request, f'Report escalated to {report.get_priority_display()}')
        
        return redirect('admin_dashboard:report-detail', pk=report.pk)

class BulkReportActionView(AdminRequiredMixin, generic.View):
    def post(self, request):
        report_ids = request.POST.getlist('report_ids')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        reports = Report.objects.filter(id__in=report_ids)
        
        if action == 'resolve':
            reports.update(
                status='resolved',
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
                admin_notes=notes
            )
            messages.success(request, f'{reports.count()} reports resolved')
        elif action == 'dismiss':
            reports.update(
                status='dismissed',
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
                admin_notes=notes
            )
            messages.success(request, f'{reports.count()} reports dismissed')
        
        return redirect('admin_dashboard:report-list')
```

### User Management Views

```python
class UserListView(AdminRequiredMixin, generic.ListView):
    model = Account
    template_name = 'admin_dashboard/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Account.objects.select_related('profile')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('-date_joined')

class UserDetailView(AdminRequiredMixin, generic.DetailView):
    model = Account
    template_name = 'admin_dashboard/user_detail.html'
    context_object_name = 'user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # User's reports (made and received)
        context['reports_made'] = Report.objects.filter(reporter=user)[:5]
        context['reports_received'] = Report.objects.filter(reported_user=user)[:5]
        
        # User's ban history
        context['ban_history'] = Ban.objects.filter(user=user)
        context['current_ban'] = Ban.objects.filter(user=user, is_active=True).first()
        
        # User's admin actions
        context['admin_actions'] = AdminActionLog.objects.filter(target_user=user)[:10]
        
        # Friend/follow stats
        from meethub.social.models import Friendship, Follow
        context['friend_count'] = Friendship.objects.filter(
            Q(requester=user) | Q(receiver=user),
            status='accepted'
        ).count()
        context['follower_count'] = Follow.objects.filter(following=user).count()
        context['following_count'] = Follow.objects.filter(follower=user).count()
        
        return context

class UserBanView(AdminRequiredMixin, generic.View):
    def post(self, request, user_id):
        user = get_object_or_404(Account, pk=user_id)
        reason = request.POST.get('reason')
        is_permanent = request.POST.get('permanent') == 'on'
        duration_days = request.POST.get('duration_days')
        
        # Deactivate any existing bans
        Ban.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Create new ban
        expires_at = None
        if not is_permanent and duration_days:
            expires_at = timezone.now() + timedelta(days=int(duration_days))
        
        Ban.objects.create(
            user=user,
            banned_by=request.user,
            reason=reason,
            is_permanent=is_permanent,
            expires_at=expires_at
        )
        
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='ban',
            target_user=user,
            reason=reason,
            details={'permanent': is_permanent, 'duration_days': duration_days}
        )
        
        messages.success(request, f'User {user.get_fullname()} has been banned')
        return redirect('admin_dashboard:user-detail', pk=user.pk)

class UserUnbanView(AdminRequiredMixin, generic.View):
    def post(self, request, user_id):
        user = get_object_or_404(Account, pk=user_id)
        
        Ban.objects.filter(user=user, is_active=True).update(is_active=False)
        
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='unban',
            target_user=user,
            reason='Ban lifted by admin'
        )
        
        messages.success(request, f'User {user.get_fullname()} has been unbanned')
        return redirect('admin_dashboard:user-detail', pk=user.pk)
```

### Admin Action Log View

```python
class AdminActionLogView(AdminRequiredMixin, generic.ListView):
    model = AdminActionLog
    template_name = 'admin_dashboard/action_log.html'
    context_object_name = 'actions'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = AdminActionLog.objects.select_related('admin', 'target_user')
        
        # Filters
        action_type = self.request.GET.get('action_type')
        admin_id = self.request.GET.get('admin_id')
        
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if admin_id:
            queryset = queryset.filter(admin_id=admin_id)
        
        return queryset
```

## 7. Admin Dashboard Forms

```python
# admin_dashboard/forms.py
from django import forms

class ReportActionForm(forms.Form):
    action = forms.ChoiceField(choices=[
        ('resolve', 'Resolve'),
        ('dismiss', 'Dismiss'),
        ('escalate', 'Escalate Priority')
    ])
    notes = forms.CharField(widget=forms.Textarea, required=False)

class UserBanForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea)
    permanent = forms.BooleanField(required=False)
    duration_days = forms.IntegerField(required=False, min_value=1, max_value=365)
```

## 8. URL Patterns

```python
# admin_dashboard/urls.py
from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.DashboardHome.as_view(), name='dashboard-home'),
    
    # Report management
    path('reports/', views.ReportListView.as_view(), name='report-list'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/action/', views.ReportActionView.as_view(), name='report-action'),
    path('reports/bulk-action/', views.BulkReportActionView.as_view(), name='bulk-report-action'),
    
    # User management
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/ban/', views.UserBanView.as_view(), name='user-ban'),
    path('users/<int:pk>/unban/', views.UserUnbanView.as_view(), name='user-unban'),
    
    # Action log
    path('action-log/', views.AdminActionLogView.as_view(), name='action-log'),
]
```

## 9. Template Structure

### Base Template

```django
<!-- admin_dashboard/templates/admin_dashboard/base.html -->
{% extends "base.html" %}

{% block content %}
<div class="admin-dashboard">
    <nav class="admin-sidebar">
        <a href="{% url 'admin_dashboard:dashboard-home' %}" class="nav-item">Dashboard</a>
        <a href="{% url 'admin_dashboard:report-list' %}" class="nav-item">Reports</a>
        <a href="{% url 'admin_dashboard:user-list' %}" class="nav-item">Users</a>
        <a href="{% url 'admin_dashboard:action-log' %}" class="nav-item">Action Log</a>
    </nav>
    
    <main class="admin-content">
        {% block admin_content %}{% endblock %}
    </main>
</div>
{% endblock %}
```

### Dashboard Home Template

```django
<!-- admin_dashboard/templates/admin_dashboard/dashboard_home.html -->
{% extends "admin_dashboard/base.html" %}

{% block admin_content %}
<h1>Admin Dashboard</h1>

<div class="stats-grid">
    <div class="stat-card">
        <h3>Total Users</h3>
        <p class="stat-value">{{ total_users }}</p>
    </div>
    <div class="stat-card">
        <h3>Active Users (30 days)</h3>
        <p class="stat-value">{{ active_users }}</p>
    </div>
    <div class="stat-card">
        <h3>Pending Reports</h3>
        <p class="stat-value">{{ pending_reports }}</p>
    </div>
    <div class="stat-card">
        <h3>Active Bans</h3>
        <p class="stat-value">{{ active_bans }}</p>
    </div>
</div>

<h2>Recent Reports</h2>
<ul class="report-list">
    {% for report in recent_reports %}
    <li>
        <a href="{% url 'admin_dashboard:report-detail' pk=report.id %}">
            {{ report.report_type }} - {{ report.reported_user }}
        </a>
        <span class="badge">{{ report.get_status_display }}</span>
    </li>
    {% endfor %}
</ul>

<h2>Recent Admin Actions</h2>
<ul class="action-list">
    {% for action in recent_actions %}
    <li>
        {{ action.admin }} - {{ action.get_action_type_display }} - {{ action.timestamp }}
    </li>
    {% endfor %}
</ul>
{% endblock %}
```

## 10. Integration with Main Project

### Add to Main URLs

```python
# meethub/urls.py
urlpatterns = [
    # ... existing paths ...
    path('admin-dashboard/', include('admin_dashboard.urls')),
]
```

### Update Settings

```python
# meethub/settings.py
INSTALLED_APPS = [
    # ... existing apps ...
    'social',
    'moderation',
    'admin_dashboard',
]
```

## 11. Ban Checking Middleware

Create middleware to check if users are banned:

```python
# admin_dashboard/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from meethub.moderation.models import Ban

class BanCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            active_ban = Ban.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            
            if active_ban and not active_ban.is_expired():
                # Allow access to logout and static files
                if request.path not in ['/logout/', '/static/']:
                    messages.error(request, 'Your account has been banned')
                    return redirect('/logout/')
        
        response = self.get_response(request)
        return response
```

Add to settings:

```python
MIDDLEWARE = [
    # ... existing middleware ...
    'admin_dashboard.middleware.BanCheckMiddleware',
]
```

## 12. Implementation Priority

### Phase 1: Admin Infrastructure
- [ ] Add `is_admin` field to Account model
- [ ] Create AdminRequiredMixin
- [ ] Create admin_dashboard app structure
- [ ] Create AdminActionLog model
- [ ] Add admin_dashboard to INSTALLED_APPS
- [ ] Add admin_dashboard URLs to main project

### Phase 2: Report Management
- [ ] Build report list view with filters
- [ ] Build report detail view
- [ ] Implement report action views (resolve, dismiss, escalate)
- [ ] Implement bulk report action view
- [ ] Create report templates
- [ ] Add admin action logging for report actions

### Phase 3: User Management
- [ ] Build user list view with search
- [ ] Build user detail view
- [ ] Implement ban/unban views
- [ ] Add user activity overview
- [ ] Create user management templates
- [ ] Add admin action logging for user actions

### Phase 4: Dashboard Home
- [ ] Create dashboard home view with stats
- [ ] Implement activity feed
- [ ] Add quick actions
- [ ] Create dashboard home template
- [ ] Add stats cards

### Phase 5: Ban Enforcement
- [ ] Create BanCheckMiddleware
- [ ] Add middleware to settings
- [ ] Test ban enforcement
- [ ] Add ban expiration checking

### Phase 6: Admin Action Log
- [ ] Build admin action log view
- [ ] Add filters for action log
- [ ] Create action log template
- [ ] Ensure all admin actions are logged

## 13. Notes

- This admin dashboard is separate from Django's built-in admin
- Django admin can still be used for direct database management
- All admin actions are logged for accountability
- Ban checking is done via middleware to ensure enforcement
- Reports can be escalated for priority handling
- Bulk actions are available for efficient moderation

---

# Implementation Notes

## Order of Implementation

You can implement these features in any order, but here's a recommended sequence:

1. **Feature Proposal 1 (Social Networking)** - Phase 1 first (core relationships)
2. **Feature Proposal 2 (Admin Dashboard)** - Phase 1 first (admin infrastructure)
3. Complete remaining phases of either feature as needed

## Dependencies

- Feature Proposal 2 depends on Feature Proposal 1's moderation models (Report, Ban)
- If implementing Feature Proposal 2 first, create basic Report and Ban models first
- Both features integrate with the existing Account and Profile models

## Testing

After each phase, test:
- Model migrations run successfully
- Views render correctly
- Forms validate properly
- Permissions work as expected
- Admin actions are logged

## Future Enhancements

Consider adding later:
- Email notifications for friend requests
- Push notifications for wall posts
- Advanced moderation AI
- Analytics dashboard
- User reputation system
- Content filtering
- Two-factor authentication for admins
