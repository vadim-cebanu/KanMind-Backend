from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)  
    repeated_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']  
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'passwords dont match'})
        
        account = User(
            email=self.validated_data['email'], 
            username=self.validated_data['fullname']
        )
        account.set_password(pw)
        account.save()
        return account
