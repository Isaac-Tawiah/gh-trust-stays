from django.db import migrations
from django.utils import timezone


def create_admin_user(apps, schema_editor):
    User = apps.get_model('users', 'User')
    
    if not User.objects.filter(phone_number='233500000003').exists():
        User.objects.create(
            phone_number='233500000003',
            first_name='Admin',
            last_name='User',
            email='admin@ghtruststays.com',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            user_type='ADMIN',
            phone_verified=True,
            email_verified=True,
            date_joined=timezone.now(),
            password='pbkdf2_sha256$600000$abc123def456ghi789jkl$m5L0qXz8VnR3wK9pY2bT6jH4cA1eF7sD0gU3wM6xZ=',
        )

def remove_admin_user(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.filter(phone_number='233500000002').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_completed_verifications_user_is_available_and_more'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, remove_admin_user),
    ]