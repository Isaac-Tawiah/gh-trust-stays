from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.property_list, name='property-list'),
    path('<uuid:property_id>/', views.property_detail, name='property-detail'),
    path('host/create/', views.create_property, name='create-property'),
    path('host/my-listings/', views.host_properties, name='host-properties'),
    path('host/<uuid:property_id>/submit/', views.submit_for_verification, name='submit-verification'),
    path('bookings/create/', views.create_booking, name='create-booking'),
    path('bookings/my-bookings/', views.my_bookings, name='my-bookings'),
    path('host/bookings/', views.host_bookings, name='host-bookings'),
    path('host/<uuid:property_id>/delete/', views.delete_property, name='delete-property'),
    path('bookings/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
]