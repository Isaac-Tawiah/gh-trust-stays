import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    Central User model for the entire platform.
    Every guest, host, hotel manager, verification agent, and admin
    is a User with a specific user_type.
    """
    
    class UserType(models.TextChoices):
        GUEST = 'GUEST', 'Guest / Traveler'
        HOST = 'HOST', 'Property Host / Landlord'
        AGENT = 'AGENT', 'Verification Agent'
        ADMIN = 'ADMIN', 'Platform Administrator'
    
    class VerificationLevel(models.TextChoices):
        NONE = 'NONE', 'Not Verified'
        BASIC = 'BASIC', 'Phone Verified'
        ID_VERIFIED = 'ID_VERIFIED', 'Government ID Verified'
        FULL = 'FULL', 'Full Background Check Complete'
    
    # Primary identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core identification
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True, unique=True, db_index=True)
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_picture = models.URLField(
        max_length=500, 
        null=True, 
        blank=True,
        help_text="URL to profile picture (stored in cloud storage later)"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Platform role - determines what this user can do
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.GUEST,
        db_index=True
    )
    
    # Trust & Verification (your entire business model)
    verification_level = models.CharField(
        max_length=20,
        choices=VerificationLevel.choices,
        default=VerificationLevel.NONE
    )
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    government_id_verified = models.BooleanField(default=False)
    government_id_type = models.CharField(max_length=50, blank=True, null=True)
    government_id_number = models.CharField(max_length=100, blank=True, null=True)
    government_id_document = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="URL to ID document (stored in cloud storage later)"
    )

        # Agent-specific fields
    is_available = models.BooleanField(
        default=True,
        help_text="Whether a verification agent is available for new assignments"
    )
    completed_verifications = models.PositiveIntegerField(default=0)
    region_of_operation = models.CharField(
        max_length=20,
        choices=[
            ('GREATER_ACCRA', 'Greater Accra'),
            ('ASHANTI', 'Ashanti'),
            ('CENTRAL', 'Central'),
            ('EASTERN', 'Eastern'),
            ('WESTERN', 'Western'),
            ('VOLTA', 'Volta'),
            ('NORTHERN', 'Northern'),
            ('UPPER_EAST', 'Upper East'),
            ('UPPER_WEST', 'Upper West'),
            ('BONO', 'Bono'),
            ('BONO_EAST', 'Bono East'),
            ('AHAFO', 'Ahafo'),
            ('SAVANNAH', 'Savannah'),
            ('NORTH_EAST', 'North East'),
            ('OTI', 'Oti'),
            ('WESTERN_NORTH', 'Western North'),
        ],
        blank=True,
        null=True
    )
    
    # Reliability metrics (your proprietary trust engine)
    trust_score = models.IntegerField(default=0, help_text="0-100 reliability score")
    completed_bookings = models.IntegerField(default=0)
    cancelled_bookings = models.IntegerField(default=0)
    host_rating_average = models.FloatField(default=0.0)
    
    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # The field used for authentication
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['user_type', 'verification_level']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_type})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_host(self):
        return self.user_type == self.UserType.HOST
    
    @property
    def is_agent(self):
        return self.user_type == self.UserType.AGENT
    
    @property
    def is_guest(self):
        return self.user_type == self.UserType.GUEST
    
    @property
    def can_list_properties(self):
        """Only verified hosts can list properties"""
        return (self.is_host and 
                self.verification_level in [
                    self.VerificationLevel.ID_VERIFIED,
                    self.VerificationLevel.FULL
                ])
    
    def update_trust_score(self):
        """
        Your proprietary trust algorithm - starts simple, can become ML-driven.
        Called whenever a booking is completed or cancelled.
        """
        score = 0
        
        if self.phone_verified:
            score += 20
        if self.email_verified:
            score += 10
        if self.government_id_verified:
            score += 30
        
        if self.completed_bookings > 0:
            total = self.completed_bookings + self.cancelled_bookings
            completion_rate = self.completed_bookings / total if total > 0 else 0
            behavior_score = int(completion_rate * 40)
            score += behavior_score
        
        self.trust_score = min(score, 100)
        self.save(update_fields=['trust_score'])