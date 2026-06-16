from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer, LoginSerializer

class RegistrationView(APIView):
    """
    POST /api/registration/
    Creates a new user and returns a token with user details.
    Status 201 on success.
    """
    permission_classes = [AllowAny]  # No Permissions required

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate or get token for the new user
            token, created = Token.objects.get_or_create(user=user)
            
            # Exact match for the requested Success Response
            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/login/
    Authenticates user and returns a token with user details.
    Status 200 on success.
    """
    permission_classes = [AllowAny]  # No Permissions required

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Generate or get token
            token, created = Token.objects.get_or_create(user=user)
            
            # Exact match for the requested Success Response
            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
