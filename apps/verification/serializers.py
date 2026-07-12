from rest_framework import serializers
from .models import VerificationAssignment, VerificationReport


class VerificationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationReport
        fields = [
            'id', 'assignment', 'verdict', 'agent_notes',
            'property_exists', 'property_matches_description',
            'photos_are_accurate', 'location_is_correct',
            'amenities_verified', 'evidence_photos', 'created_at'
        ]
        read_only_fields = ['assignment', 'created_at']


class VerificationAssignmentSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    property_city = serializers.CharField(source='property.city', read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    report = VerificationReportSerializer(read_only=True)

    class Meta:
        model = VerificationAssignment
        fields = [
            'id', 'property', 'property_name', 'property_city',
            'agent', 'agent_name', 'status',
            'assigned_at', 'accepted_at', 'completed_at',
            'notes', 'report'
        ]
        read_only_fields = ['status', 'assigned_at', 'accepted_at', 'completed_at']