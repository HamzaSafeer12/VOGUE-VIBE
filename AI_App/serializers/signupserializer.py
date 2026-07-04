from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Profile

class SignupSerializer(serializers.ModelSerializer):
    # Profile ki extra fields
    phone_number = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'address']

    def create(self, validated_data):
        # 1.profile fields
        phone = validated_data.pop('phone_number', '')
        address = validated_data.pop('address', '')
        
        # 2. User create (Password hashing ke saath)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        # 3. create profile which is connect with user
        Profile.objects.create(
            user=user, 
            phone_number=phone, 
            address=address
        )
        
        return user