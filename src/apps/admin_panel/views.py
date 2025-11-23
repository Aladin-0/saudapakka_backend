from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

# Import models from other apps
from apps.properties.models import Property
from apps.users.models import BrokerProfile, KycVerification

User = get_user_model()

# --- Custom Permission: Super Admin Only ---
class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

# ==========================================
# 1. ANALYTICS & STATS (For Dashboard Graphs)
# ==========================================

class AdminDashboardStats(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        today = timezone.now().date()
        last_30_days = timezone.now() - timedelta(days=30)

        return Response({
            "users": {
                "total": User.objects.count(),
                "sellers": User.objects.filter(is_active_seller=True).count(),
                "brokers": User.objects.filter(is_active_broker=True).count(),
                "new_this_month": User.objects.filter(date_joined__gte=last_30_days).count()
            },
            "properties": {
                "total": Property.objects.count(),
                "pending": Property.objects.filter(verification_status='PENDING').count(),
                "verified": Property.objects.filter(verification_status='VERIFIED').count(),
                "rejected": Property.objects.filter(verification_status='REJECTED').count(),
            },
            "revenue_simulation": {
                # Placeholder if you add monetization later
                "total_deals_closed": 0 
            }
        })

# ==========================================
# 2. PROPERTY VERIFICATION WORKFLOW
# ==========================================

class AdminPropertyList(generics.ListAPIView):
    """
    List properties based on status.
    Usage: /api/admin/properties/?status=PENDING
    """
    permission_classes = [IsSuperAdmin]
    # We need to import the serializer. We will do this in the serializers step.
    # For now, we assume PropertySerializer exists.
    from apps.properties.serializers import PropertySerializer 
    serializer_class = PropertySerializer

    def get_queryset(self):
        status_param = self.request.query_params.get('status', 'PENDING')
        return Property.objects.filter(verification_status=status_param).order_by('-created_at')

class AdminPropertyAction(APIView):
    """
    Approve or Reject a property.
    """
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        try:
            property_obj = Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            return Response({"error": "Property not found"}, status=404)

        action = request.data.get('action') # 'APPROVE' or 'REJECT'
        reason = request.data.get('reason', '')

        if action == 'APPROVE':
            property_obj.verification_status = 'VERIFIED'
            property_obj.rejection_reason = None
            property_obj.save()
            return Response({"message": f"Property '{property_obj.title}' is now LIVE."})

        elif action == 'REJECT':
            property_obj.verification_status = 'REJECTED'
            property_obj.rejection_reason = reason
            property_obj.save()
            return Response({"message": f"Property rejected."})

        return Response({"error": "Invalid action. Use APPROVE or REJECT"}, status=400)

# ==========================================
# 3. USER MANAGEMENT (Brokers/Sellers)
# ==========================================

class AdminUserList(generics.ListAPIView):
    """
    List all users with filters.
    Usage: /api/admin/users/?role=BROKER
    """
    permission_classes = [IsSuperAdmin]
    from apps.users.serializers import UserSerializer
    serializer_class = UserSerializer

    def get_queryset(self):
        role = self.request.query_params.get('role', 'ALL')
        if role == 'BROKER':
            return User.objects.filter(is_active_broker=True)
        elif role == 'SELLER':
            return User.objects.filter(is_active_seller=True)
        return User.objects.all()

class AdminUserAction(APIView):
    """
    Ban or Activate a user.
    """
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        action = request.data.get('action') # 'BLOCK' or 'UNBLOCK'
        
        if action == 'BLOCK':
            user.is_active = False
            user.save()
            return Response({"message": "User blocked successfully"})
        elif action == 'UNBLOCK':
            user.is_active = True
            user.save()
            return Response({"message": "User unblocked"})
            
        return Response({"error": "Invalid action"}, status=400)