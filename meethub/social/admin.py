from django.contrib import admin
from .models import Friendship, Follow, Block


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
