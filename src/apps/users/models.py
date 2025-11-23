import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # CHANGED: Email is now required and unique
    email = models.EmailField(unique=True) 
    phone_number = models.CharField(max_length=15, blank=True, null=True) # Optional now
    
    is_active_seller = models.BooleanField(default=False)
    is_active_broker = models.BooleanField(default=False)
    
    # We also need a field to store the OTP temporarily
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'  # Login with Email
    REQUIRED_FIELDS = ['username', 'phone_number']

    # Fix conflicts (Keep these as they were)
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set', blank=True)

class KycVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    aadhaar_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    digilocker_json = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20, 
        choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')],
        default='PENDING'
    )

class BrokerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    services_offered = models.JSONField(default=list)
    experience_years = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)

