from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom manager for our User model where phone number is the 
    primary identifier, not username.
    """
    
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required for all users')
        
        phone_number = self.normalize_phone(phone_number)
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'ADMIN')
        extra_fields.setdefault('phone_verified', True)
        
        return self.create_user(phone_number, password, **extra_fields)
    
    @staticmethod
    def normalize_phone(phone_number):
        """Normalize Ghanaian phone numbers to +233 format"""
        number = ''.join(filter(str.isdigit, str(phone_number)))
        
        if number.startswith('0'):
            number = '+233' + number[1:]
        elif not number.startswith('233'):
            number = '+233' + number
        
        return number