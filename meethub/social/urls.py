from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('friend-request/send/<int:user_id>/', views.SendFriendRequest.as_view(), name='send-friend-request'),
    path('friend-request/accept/<int:friendship_id>/', views.AcceptFriendRequest.as_view(), name='accept-friend-request'),
    path('friend-request/reject/<int:friendship_id>/', views.RejectFriendRequest.as_view(), name='reject-friend-request'),
    path('unfriend/<int:user_id>/', views.Unfriend.as_view(), name='unfriend'),
    path('follow/<int:user_id>/', views.FollowUser.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', views.UnfollowUser.as_view(), name='unfollow-user'),
    path('block/<int:user_id>/', views.BlockUser.as_view(), name='block-user'),
    path('unblock/<int:user_id>/', views.UnblockUser.as_view(), name='unblock-user'),
]
