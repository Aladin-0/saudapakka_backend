import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings

def get_expiry():
    return timezone.now() + timedelta(hours=48)

class Mandate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='seller_mandates', on_delete=models.CASCADE)
    broker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='broker_mandates', null=True, blank=True, on_delete=models.SET_NULL)
    
    DEAL_TYPES = [('WITH_BROKER', 'With Broker'), ('WITH_PLATFORM', 'With Platform')]
    deal_type = models.CharField(max_length=20, choices=DEAL_TYPES)
    
    INITIATED_BY = [('SELLER', 'Seller'), ('BROKER', 'Broker')]
    initiated_by = models.CharField(max_length=10, choices=INITIATED_BY)
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiry)
