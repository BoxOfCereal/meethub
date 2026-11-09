from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Friendship


@receiver(post_save, sender=Friendship)
def friendship_accepted_notification(sender, instance, created, **kwargs):
    """Send notification when friendship is accepted"""
    if not created and instance.status == 'accepted':
        # Create notification for both users
        # Note: This requires a notifications app to be implemented
        # For now, this is a placeholder for future notification system
        try:
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
        except ImportError:
            # Notifications app not implemented yet
            pass
