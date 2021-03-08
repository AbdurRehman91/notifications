from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings

class Notifications(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE,
        null=True,related_name='notifications')
    # Not all notifications will have a sender.
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='notifications_sender')
    subject = models.CharField(max_length=255, blank=True, null=True)
    notification_type = models.CharField(max_length=100, blank=True, null=True)
    INDIVIDUAL, GROUP = 'Individual', 'Group'
    choices = (
        (INDIVIDUAL, 'Individual'),
        (GROUP, 'Group')
    )
    category = models.CharField(max_length=15, blank=True, choices=choices, db_index=True)
    body = models.TextField(null=True)
    date_sent = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    date_read = models.DateTimeField(blank=True, null=True)
    notification_language = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        ordering = ('-date_sent',)
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
    
    def __str__(self):
        return self.subject

    @property
    def is_read(self):
        return self.date_read is not None

