import email
from rest_framework import serializers
from .models import UserAccount
from .utils import send_email

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'name', 'password', 'confirm_password']
        

    def validate(self,data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password or confirm_password:
            if password != confirm_password:
              raise serializers.ValidationError('Passwords do not match')
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = UserAccount.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        send_email(
            user.name, 
            user.email
        )
        return user
    


class RealtorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'name', 'password']

    def create(self, validated_data):
        return UserAccount.objects.create_realtor(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['name', 'email']

