from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/properties/', include('apps.properties.urls')),
    path('api/verification/', include('apps.verification.urls')),
    path('api/payments/', include('apps.payments.urls')),
]