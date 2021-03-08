from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from notifications.utils import year_ahead

class User(AbstractUser):
    mobile_number = PhoneNumberField(max_length=15, null=True, blank=True, unique=True, db_index=True)
    is_active = models.BooleanField(_('active'), default=True)


class UserDevices(models.Model):
    push_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey('User', null=True, on_delete=models.CASCADE, related_name="devices")
    validity = models.DateField(default=year_ahead)
    def is_active(self):
        """
        Check if user device information is active. Validity is set to year ahead at time of instance creation

        Returns
        -------
        bool
            True if active, False otherwise
        """
        return self.validity > datetime.now().date()
    
    def __str__(self):
        return self.device_type