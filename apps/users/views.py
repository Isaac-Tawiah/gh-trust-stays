from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Registration successful!',
            'token': token.key,
            'user': {
                'id': str(user.id),
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'user_type': user.user_type
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    
    if not phone_number or not password:
        return Response(
            {'error': 'Phone number and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(phone_number=phone_number, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'message': 'Login successful.',
        'token': token.key,
        'user': {
            'id': str(user.id),
            'phone_number': user.phone_number,
            'first_name': user.first_name,
            'user_type': user.user_type,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def setup_admin(request):
    phone = '233500000001'
    password = 'admin123456'
    
    user, created = User.objects.get_or_create(
        phone_number=phone,
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'user_type': 'ADMIN',
        }
    )
    
    if not created:
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.user_type = 'ADMIN'
        user.save()
    
    return Response({
        'message': 'Admin ready.',
        'phone': phone,
        'password': password,
    })