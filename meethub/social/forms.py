from django import forms
from .models import Friendship, Follow, Block


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
