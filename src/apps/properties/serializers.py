from rest_framework import serializers
from .models import Property, PropertyImage, SavedProperty, RecentlyViewed
from apps.users.serializers import UserSerializer # Ensure you have a basic UserSerializer

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_thumbnail']

class PropertySerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.full_name')
    owner_id = serializers.ReadOnlyField(source='owner.id')
    images = PropertyImageSerializer(many=True, read_only=True)
    
    # We return Booleans for docs to Frontend to show "Tick Marks"
    has_7_12 = serializers.SerializerMethodField()
    has_mojani = serializers.SerializerMethodField()
    # ... (You can add others similarly)

    class Meta:
        model = Property
        fields = [
            'id', 'owner_name', 'owner_id', 'title', 'description', 'price', 
            'property_type', 'listing_type', 'address_line', 'latitude', 'longitude',
            'verification_status', 'rejection_reason',
            'created_at', 'images', 
            # Documents (For owner/admin to see actual link)
            'doc_7_12', 'doc_mojani', 'doc_na_order', 
            'doc_layout_order', 'doc_layout_copy', 
            'doc_building_perm', 'doc_floor_plan',
            # Trust Indicators (For buyers)
            'has_7_12', 'has_mojani'
        ]
        read_only_fields = ['verification_status', 'rejection_reason', 'created_at']

    def get_has_7_12(self, obj): return bool(obj.doc_7_12)
    def get_has_mojani(self, obj): return bool(obj.doc_mojani)