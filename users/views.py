from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import UserAccount
from .serializers import UserSerializer, RealtorRegisterSerializer, UserUpdateSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()  # 🔥 THIS triggers create() + send_email

        return Response(
            {'success': 'User created successfully', 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )

    
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            {'user': serializer.data},
            status=status.HTTP_200_OK
        )
    
    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
       )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'user': UserSerializer(request.user).data},
            status=status.HTTP_200_OK
        )
    
    def put(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'error': 'Old password and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
        )

        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
        )

        request.user.set_password(new_password)
        request.user.save()

        return Response(
            {'success': 'Password updated successfully'},
            status=status.HTTP_200_OK
       )


    
    def delete(self, request):
        password = request.data.get('password')

        if not password:
            return Response(
                {'error': 'Password is required to delete account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(password):
            return Response(
                {'error': 'Incorrect password'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        request.user.delete()

        return Response(
            {'success': 'User deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    