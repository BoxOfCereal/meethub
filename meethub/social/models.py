from django.db import models
from django.core.exceptions import ValidationError
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
    
    def clean(self):
        if self.requester == self.receiver:
            raise ValidationError("Cannot send friend request to yourself")
        super().clean()
    
    def __str__(self):
        return f"{self.requester} -> {self.receiver} ({self.status})"


class Follow(models.Model):
    follower = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
    
    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Cannot follow yourself")
        super().clean()
    
    def __str__(self):
        return f"{self.follower} follows {self.following}"


class Block(models.Model):
    blocker = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blocker', 'blocked']
    
    def clean(self):
        if self.blocker == self.blocked:
            raise ValidationError("Cannot block yourself")
        super().clean()
    
    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"
