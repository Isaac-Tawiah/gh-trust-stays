from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'phone_number', 
        'first_name', 
        'last_name', 
        'user_type', 
        'verification_level',
        'trust_score',
        'is_active'
    )
    list_filter = ('user_type', 'verification_level', 'is_active', 'phone_verified')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Login Credentials', {
            'fields': ('phone_number', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'profile_picture', 'date_of_birth')
        }),
        ('Platform Role & Verification', {
            'fields': (
                'user_type', 
                'verification_level',
                'phone_verified',
                'email_verified',
                'government_id_verified',
                'government_id_type',
                'government_id_number',
                'government_id_document',
            )
        }),
        ('Trust & Reliability', {
            'fields': ('trust_score', 'completed_bookings', 'cancelled_bookings', 'host_rating_average')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 
                'first_name', 
                'last_name', 
                'password1', 
                'password2',
                'user_type'
            ),
        }),
    )