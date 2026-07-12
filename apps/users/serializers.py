from rest_framework import serializers
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'phone_number', 
            'first_name', 
            'last_name', 
            'email',
            'password',
            'user_type'
        ]
        extra_kwargs = {
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'first_name',
            'last_name',
            'email',
            'user_type',
            'verification_level',
            'trust_score',
            'profile_picture',
            'date_joined'
        ]
        read_only_fields = ['id', 'verification_level', 'trust_score', 'date_joined']