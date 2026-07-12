from django.contrib import admin
from .models import VerificationAssignment, VerificationReport


@admin.register(VerificationAssignment)
class VerificationAssignmentAdmin(admin.ModelAdmin):
    list_display = ('property', 'agent', 'status', 'assigned_at', 'completed_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('property__name', 'agent__first_name', 'agent__last_name')


@admin.register(VerificationReport)
class VerificationReportAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'verdict', 'property_exists', 'created_at')
    list_filter = ('verdict', 'property_exists')