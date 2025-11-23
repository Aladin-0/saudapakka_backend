from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q  # <--- CRITICAL: Needed for the OR logic

from .models import Property, PropertyImage, SavedProperty, RecentlyViewed
from .serializers import PropertySerializer, PropertyImageSerializer
from .permissions import IsOwnerOrReadOnly

class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    # 1. Must be Authenticated to Create/Update
    # 2. Must be Owner to Update/Delete (Edit/Delete your own listing)
    # 3. Anyone can View (GET)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser] # Allows file uploads
    
    # Filter Configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'price': ['gte', 'lte'],  # price__gte=1000, price__lte=5000
        'property_type': ['exact'],
        'listing_type': ['exact'],
    }
    search_fields = ['title', 'address_line', 'description']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        """
        Logic for Visibility:
        1. Admin: Sees EVERYTHING.
        2. Seller/Broker (Owner): Sees Public VERIFIED items + Their OWN items (Pending/Rejected).
        3. Public (Guest/Buyer): Sees only VERIFIED items.
        """
        
        # 1. Admin Logic
        if self.request.user.is_staff:
            return Property.objects.all().order_by('-created_at')
        
        # 2. Logged In User Logic (Seller, Broker, or Buyer)
        if self.request.user.is_authenticated:
            return Property.objects.filter(
                # Logic: Show if it is VERIFIED ... OR ... if I am the OWNER
                Q(verification_status='VERIFIED') | Q(owner=self.request.user)
            ).distinct().order_by('-created_at')
            
        # 3. Guest Logic
        return Property.objects.filter(verification_status='VERIFIED').order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        
        # CHECK: To upload, you MUST be an Active Seller OR Active Broker
        if not (user.is_active_seller or user.is_active_broker):
            raise permissions.PermissionDenied(
                "Restricted: You must complete KYC and become a Seller or Broker to post listings."
            )
        
        # If valid, save it with 'PENDING' status
        serializer.save(owner=user, verification_status='PENDING')

    # --- Custom Actions (Save, Recent, etc.) ---

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def save_property(self, request, pk=None):
        """Toggle Save/Unsave"""
        property_obj = self.get_object()
        saved_item, created = SavedProperty.objects.get_or_create(user=request.user, property=property_obj)
        if not created:
            saved_item.delete()
            return Response({'message': 'Property removed from saved'}, status=200)
        return Response({'message': 'Property saved'}, status=201)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def record_view(self, request, pk=None):
        """Frontend calls this when user opens details page"""
        property_obj = self.get_object()
        RecentlyViewed.objects.update_or_create(user=request.user, property=property_obj)
        
        # Return details normally
        serializer = self.get_serializer(property_obj)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_saved(self, request):
        """Get list of properties saved by current user"""
        saved = SavedProperty.objects.filter(user=request.user).select_related('property')
        props = [s.property for s in saved]
        serializer = self.get_serializer(props, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_recent(self, request):
        """Get list of last 10 properties viewed by current user"""
        recent = RecentlyViewed.objects.filter(user=request.user).order_by('-viewed_at')[:10]
        props = [r.property for r in recent]
        serializer = self.get_serializer(props, many=True)
        return Response(serializer.data)