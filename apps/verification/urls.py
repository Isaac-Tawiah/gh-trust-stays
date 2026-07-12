from django.urls import path
from . import views

urlpatterns = [
    path('admin/assign/', views.assign_agent, name='assign-agent'),
    path('admin/pending/', views.pending_verifications, name='pending-verifications'),
    path('agent/assignments/', views.agent_assignments, name='agent-assignments'),
    path('agent/<uuid:assignment_id>/accept/', views.accept_assignment, name='accept-assignment'),
    path('agent/<uuid:assignment_id>/report/', views.submit_report, name='submit-report'),
]