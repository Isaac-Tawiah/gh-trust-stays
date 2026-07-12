from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.properties.models import Property
from apps.properties.choices import PropertyStatus
from .models import VerificationAssignment, VerificationReport
from .serializers import VerificationAssignmentSerializer, VerificationReportSerializer


# ──────────────────────────────────────
# ADMIN ENDPOINTS
# ──────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_agent(request):
    property_id = request.data.get('property_id')
    agent_id = request.data.get('agent_id')
    notes = request.data.get('notes', '')

    if not property_id or not agent_id:
        return Response({'error': 'property_id and agent_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

    prop = get_object_or_404(Property, id=property_id, status=PropertyStatus.PENDING_VERIFICATION)

    if hasattr(prop, 'verification'):
        return Response({'error': 'This property already has a verification assignment.'}, status=status.HTTP_400_BAD_REQUEST)

    from apps.users.models import User
    agent = get_object_or_404(User, id=agent_id, user_type='AGENT', is_active=True)

    assignment = VerificationAssignment.objects.create(
        property=prop,
        agent=agent,
        assigned_by=request.user,
        notes=notes
    )

    serializer = VerificationAssignmentSerializer(assignment)
    return Response({'message': 'Agent assigned.', 'assignment': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_verifications(request):
    props = Property.objects.filter(status=PropertyStatus.PENDING_VERIFICATION)
    data = [{'id': str(p.id), 'name': p.name, 'city': p.city, 'host_name': p.host.get_full_name()} for p in props]
    return Response({'count': len(data), 'results': data})


# ──────────────────────────────────────
# AGENT ENDPOINTS
# ──────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_assignments(request):
    if not request.user.is_agent:
        return Response({'error': 'Only verification agents can view assignments.'}, status=status.HTTP_403_FORBIDDEN)

    assignments = VerificationAssignment.objects.filter(agent=request.user)
    serializer = VerificationAssignmentSerializer(assignments, many=True)
    return Response({'count': assignments.count(), 'results': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_assignment(request, assignment_id):
    if not request.user.is_agent:
        return Response({'error': 'Only verification agents can accept assignments.'}, status=status.HTTP_403_FORBIDDEN)

    assignment = get_object_or_404(
        VerificationAssignment,
        id=assignment_id,
        agent=request.user,
        status='ASSIGNED'
    )

    assignment.status = 'ACCEPTED'
    assignment.accepted_at = assignment.accepted_at or assignment.accepted_at
    from django.utils import timezone
    assignment.accepted_at = timezone.now()
    assignment.save(update_fields=['status', 'accepted_at'])

    return Response({'message': 'Assignment accepted.', 'status': assignment.status})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_report(request, assignment_id):
    if not request.user.is_agent:
        return Response({'error': 'Only verification agents can submit reports.'}, status=status.HTTP_403_FORBIDDEN)

    assignment = get_object_or_404(
        VerificationAssignment,
        id=assignment_id,
        agent=request.user,
        status__in=['ACCEPTED', 'IN_PROGRESS']
    )

    if hasattr(assignment, 'report'):
        return Response({'error': 'A report already exists for this assignment.'}, status=status.HTTP_400_BAD_REQUEST)

    report = VerificationReport.objects.create(
        assignment=assignment,
        verdict=request.data.get('verdict'),
        agent_notes=request.data.get('agent_notes', ''),
        property_exists=request.data.get('property_exists', True),
        property_matches_description=request.data.get('property_matches_description', True),
        photos_are_accurate=request.data.get('photos_are_accurate', True),
        location_is_correct=request.data.get('location_is_correct', True),
        amenities_verified=request.data.get('amenities_verified', {}),
        evidence_photos=request.data.get('evidence_photos', [])
    )

    serializer = VerificationReportSerializer(report)
    return Response({
        'message': 'Report submitted. Property is now LIVE.' if report.verdict == 'APPROVED' else 'Report submitted.',
        'report': serializer.data
    }, status=status.HTTP_201_CREATED)