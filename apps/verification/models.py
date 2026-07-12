import uuid
from django.db import models
from django.conf import settings
from apps.properties.models import Property


class VerificationAssignment(models.Model):

    class AssignmentStatus(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        ACCEPTED = 'ACCEPTED', 'Accepted by Agent'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='verification')
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verification_assignments',
        limit_choices_to={'user_type': 'AGENT'}
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_made',
        limit_choices_to={'user_type': 'ADMIN', 'is_staff': True}
    )
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes from admin to agent")

    class Meta:
        verbose_name = 'Verification Assignment'
        verbose_name_plural = 'Verification Assignments'
        ordering = ['-assigned_at']

    def __str__(self):
        return f"Verification: {self.property.name} - {self.status}"


class VerificationReport(models.Model):

    class Verdict(models.TextChoices):
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        NEEDS_CLARIFICATION = 'NEEDS_CLARIFICATION', 'Needs Clarification'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.OneToOneField(VerificationAssignment, on_delete=models.CASCADE, related_name='report')
    verdict = models.CharField(max_length=25, choices=Verdict.choices)
    agent_notes = models.TextField()
    property_exists = models.BooleanField(default=True)
    property_matches_description = models.BooleanField(default=True)
    photos_are_accurate = models.BooleanField(default=True)
    location_is_correct = models.BooleanField(default=True)
    amenities_verified = models.JSONField(default=dict, help_text="Which amenities were confirmed on-site")
    evidence_photos = models.JSONField(default=list, help_text="List of photo URLs taken during inspection")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Verification Report'
        verbose_name_plural = 'Verification Reports'

    def __str__(self):
        return f"Report: {self.assignment.property.name} - {self.verdict}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new and self.verdict == 'APPROVED':
            prop = self.assignment.property
            prop.status = 'LIVE'
            prop.save(update_fields=['status'])

            self.assignment.status = 'COMPLETED'
            self.assignment.completed_at = self.created_at
            self.assignment.save(update_fields=['status', 'completed_at'])

            agent = self.assignment.agent
            if agent:
                agent.completed_verifications += 1
                agent.save(update_fields=['completed_verifications'])