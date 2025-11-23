from django.urls import path
from .views import SendOtpView, VerifyOtpView, KycSubmissionView, UpgradeRoleView, SearchProfileView, AdminDashboardStats, UserProfileView

urlpatterns = [
    path('auth/login/', SendOtpView.as_view(), name='login-otp'),
    path('auth/verify/', VerifyOtpView.as_view(), name='verify-otp'),
    
    # New Endpoints for KYC and Role Upgrade
    path('kyc/submit/', KycSubmissionView.as_view(), name='submit-kyc'),
    path('user/upgrade/', UpgradeRoleView.as_view(), name='upgrade-role'),
    path('search-profiles/', SearchProfileView.as_view(), name='search-profiles'),
    path('admin/stats/', AdminDashboardStats.as_view(), name='admin-stats'),
    path('user/me/', UserProfileView.as_view(), name='user-profile'),
]