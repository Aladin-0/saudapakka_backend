from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import User
import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import status, permissions
from .serializers import UserSerializer # Ensure you have this
from django.contrib.auth import get_user_model

from .models import User, KycVerification, BrokerProfile
from apps.properties.models import Property  # <--- Added Property model import

User = get_user_model()

class SendOtpView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # 2. Get or Create User
        # We use 'username' as email because AbstractUser requires a username
        user, created = User.objects.get_or_create(email=email, defaults={'username': email})
        
        # 3. Save OTP to DB
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # 4. Send Email (This will print to Console in dev)
        send_mail(
            subject='Your SaudaPakka Login OTP',
            message=f'Your OTP is: {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'OTP sent successfully! Check your console.'})

class VerifyOtpView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # 1. Check if OTP matches
        if user.otp != otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check Expiry (Example: 5 mins validity)
        if (timezone.now() - user.otp_created_at).total_seconds() > 300:
             return Response({'error': 'OTP Expired'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Clear OTP
        user.otp = None
        user.save()

        # 4. Generate JWT Token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'is_active_seller': user.is_active_seller,
                'is_active_broker': user.is_active_broker
            }
        })

class KycSubmissionView(APIView):
    permission_classes = [IsAuthenticated]  # <--- User must be logged in

    def post(self, request):
        data = request.data
        
        # 1. Get or Create the KYC record for this user
        kyc, created = KycVerification.objects.get_or_create(user=request.user)
        
        # 2. Save Simulated Data
        kyc.aadhaar_number = data.get('aadhaar_number', '')
        kyc.pan_number = data.get('pan_number', '')
        kyc.digilocker_json = data.get('digilocker_json', {}) # Save the full JSON
        
        # 3. Simulate Instant Verification (In real life, this checks the docs)
        kyc.status = 'VERIFIED'
        kyc.save()

        return Response({
            "message": "KYC Details Submitted and Verified successfully",
            "status": kyc.status
        })

class UpgradeRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role_to_add = request.data.get('role') # Expecting 'SELLER' or 'BROKER'

        # 1. Check if KYC is verified
        try:
            kyc = request.user.kycverification
            if kyc.status != 'VERIFIED':
                return Response({"error": "KYC not verified. Please complete KYC first."}, status=400)
        except KycVerification.DoesNotExist:
            return Response({"error": "No KYC record found. Please complete KYC first."}, status=400)

        # 2. Upgrade Logic
        if role_to_add == 'SELLER':
            request.user.is_active_seller = True
            request.user.save()
            return Response({"message": "Congratulations! You are now a Seller."})

        elif role_to_add == 'BROKER':
            request.user.is_active_broker = True
            request.user.save()
            # Create empty broker profile if not exists
            BrokerProfile.objects.get_or_create(user=request.user)
            return Response({"message": "Congratulations! You are now a Broker."})

        else:
            return Response({"error": "Invalid role. Choose 'SELLER' or 'BROKER'"}, status=400)

class SearchProfileView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer # You might want a simpler serializer for public view

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        role = self.request.query_params.get('role', 'BROKER') # Default search Broker

        queryset = User.objects.all()

        if role == 'BROKER':
            queryset = queryset.filter(is_active_broker=True)
        elif role == 'SELLER':
            queryset = queryset.filter(is_active_seller=True)

        if query:
            # Search by Name or ID (UUID)
            if len(query) > 20: # Assuming it's a UUID
                queryset = queryset.filter(id=query)
            else:
                queryset = queryset.filter(full_name__icontains=query)
        
        return queryset
    
# Add to src/apps/users/views.py

class AdminDashboardStats(APIView):
    permission_classes = [permissions.IsAdminUser] # STRICTLY ADMIN ONLY

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "active_sellers": User.objects.filter(is_active_seller=True).count(),
            "active_brokers": User.objects.filter(is_active_broker=True).count(),
            "total_properties": Property.objects.count(),
            "pending_properties": Property.objects.filter(verification_status='PENDING').count(),
            "verified_properties": Property.objects.filter(verification_status='VERIFIED').count(),
        })

class UserProfileView(APIView):
    """
    Get or Update the logged-in user's details.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Return full user details + KYC status + Broker Profile
        serializer = UserSerializer(request.user)
        data = serializer.data
        
        # Add extra context (KYC status)
        try:
            data['kyc_status'] = request.user.kycverification.status
        except:
            data['kyc_status'] = 'NOT_SUBMITTED'
            
        return Response(data)

    def patch(self, request):
        # Allow updating Name and Email
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
