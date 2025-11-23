from rest_framework import serializers
from .models import User, KycVerification, BrokerProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'full_name', 
            'email', 
            'phone_number', 
            'is_active_seller', 
            'is_active_broker'
        ]

class KycVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KycVerification
        fields = ['aadhaar_number', 'pan_number', 'status']

class BrokerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerProfile
        fields = ['services_offered', 'experience_years', 'is_verified']
