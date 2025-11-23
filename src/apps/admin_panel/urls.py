from django.urls import path
from .views import (
    AdminDashboardStats,
    AdminPropertyDetail, 
    AdminPropertyList, 
    AdminPropertyAction,
    AdminUserList,
    AdminUserAction ,
    
)

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', AdminDashboardStats.as_view(), name='admin-stats'),

    # Property Management
    path('properties/', AdminPropertyList.as_view(), name='admin-prop-list'),
    path('properties/<uuid:pk>/action/', AdminPropertyAction.as_view(), name='admin-prop-action'),

    # User Management
    path('users/', AdminUserList.as_view(), name='admin-user-list'),
    path('users/<uuid:pk>/action/', AdminUserAction.as_view(), name='admin-user-action'),

    # View Single Property (Details + Docs)
    path('properties/<uuid:pk>/', AdminPropertyDetail.as_view(), name='admin-prop-detail'),
]