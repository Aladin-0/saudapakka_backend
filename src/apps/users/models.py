import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # --- MISSING FIELD ADDED HERE ---
    full_name = models.CharField(max_length=255, blank=True, default='') 
    
    is_active_seller = models.BooleanField(default=False)
    is_active_broker = models.BooleanField(default=False)
    
    # OTP Fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # 'full_name' is not required for admin creation, but required for app usage

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

