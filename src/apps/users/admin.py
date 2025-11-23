from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, KycVerification, BrokerProfile

admin.site.register(User, UserAdmin)
admin.site.register(KycVerification)
admin.site.register(BrokerProfile)