import uuid
from django.db import models
from pgvector.django import VectorField
from django.conf import settings

class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # --- Basic Details ---
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    
    # --- Expanded Property Types ---
    PROPERTY_TYPES = [
        ('FLAT', 'Flat/Apartment'),
        ('LAND', 'Residential Land'),
        ('SERVICED_APT', 'Serviced Apartments'),
        ('BUILDER_FLOOR', 'Independent/Builder Floor'),
        ('STUDIO', '1 RK/Studio Apartment'),
        ('VILLA', 'Independent House/Villa'),
        ('FARMHOUSE', 'Farm House'),
        ('OTHER', 'Other'),
    ]
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    
    LISTING_TYPES = [('SELL', 'Sell'), ('RENT', 'Rent'), ('NEW_LAUNCH', 'New Launch')]
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES)
    
    # --- Location & Map ---
    address_line = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # --- Documents (PDFs) - Optional but builds trust ---
    # We use FileField. In production, these should go to S3/Cloudinary.
    doc_7_12 = models.FileField(upload_to='docs/7_12/', null=True, blank=True)
    doc_mojani = models.FileField(upload_to='docs/mojani/', null=True, blank=True)
    doc_na_order = models.FileField(upload_to='docs/na_order/', null=True, blank=True)
    doc_layout_order = models.FileField(upload_to='docs/layout_order/', null=True, blank=True)
    doc_layout_copy = models.FileField(upload_to='docs/layout_copy/', null=True, blank=True)
    doc_building_perm = models.FileField(upload_to='docs/building_perm/', null=True, blank=True)
    doc_floor_plan = models.FileField(upload_to='docs/floor_plan/', null=True, blank=True)

    # --- Verification Logic ---
    VERIFICATION_STATUS = [
        ('PENDING', 'Pending Review'),
        ('VERIFIED', 'Verified & Live'),
        ('REJECTED', 'Rejected')
    ]
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING')
    rejection_reason = models.TextField(null=True, blank=True) # If admin rejects, say why

    # --- Search ---
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='properties/')
    is_thumbnail = models.BooleanField(default=False)

# --- NEW: User Interactions ---

class SavedProperty(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property') # Prevent saving same prop twice

class RecentlyViewed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True) # Updates time if viewed again
