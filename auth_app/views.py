from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .api.serializers import RegistrationSerializer, LoginSerializer
from rest_framework import status


class RegistrationView(APIView):
    permission_classes= [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            return Response({
                'token': token.key,
                'fullname': saved_account.first_name,
                'email': saved_account.email,
                'user_id': saved_account.id
            }, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            


class LoginView(APIView):
    permission_classes= [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "fullname": user.first_name,
            "email": user.email,
            "user_id": user.id
            }, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                

