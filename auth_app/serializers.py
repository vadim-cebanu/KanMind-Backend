from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration matching the German API specification.
    """
    repeated_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate(self, attrs):
        """
        Validate that password and repeated_password match.
        
        Args:
            attrs: Dictionary of validated field data
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        
        Args:
            validated_data: Dictionary of validated field data
            
        Returns:
            Newly created User instance
        """
        return User.objects.create_user(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password'],
            repeated_password=validated_data['repeated_password']
        )


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication matching the German API specification.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """
        Validate user credentials and authenticate.
        
        Args:
            data: Dictionary containing email and password
            
        Returns:
            Validated data with authenticated user
            
        Raises:
            ValidationError: If credentials are invalid or user is inactive
        """
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Must include both 'email' and 'password'.")

        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid credentials!")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data['user'] = user
        return data