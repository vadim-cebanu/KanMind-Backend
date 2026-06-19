from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as the unique identifier.
    """
    def create_user(self, email, fullname, password=None, repeated_password=None, **extra_fields):
        """
        Create and save a regular user with the given email, fullname and password.
        
        Args:
            email: User's email address (unique identifier)
            fullname: User's full name
            password: User's password
            repeated_password: Password confirmation (must match password)
            **extra_fields: Additional fields for the user
            
        Returns:
            User instance
            
        Raises:
            ValueError: If email is missing or passwords don't match
        """
        if not email:
            raise ValueError("Users must have an email address")
        if password != repeated_password:
            raise ValueError("Passwords don't match")

        user = self.model(
            email=self.normalize_email(email),
            fullname=fullname,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, fullname and password.
        
        Args:
            email: Superuser's email address
            fullname: Superuser's full name
            password: Superuser's password
            **extra_fields: Additional fields
            
        Returns:
            User instance with is_admin=True
        """
        extra_fields.setdefault('is_admin', True)
        user = self.create_user(email, fullname, password, repeated_password=password, **extra_fields)
        return user

class User(AbstractBaseUser):
    """
    Custom user model using email as the unique identifier instead of username.
    """
    email = models.EmailField(verbose_name="Email", max_length=300, unique=True)
    fullname = models.CharField(verbose_name="Full Name", max_length=200)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]  

    def __str__(self):
        """Return string representation of user (email)."""
        return self.email

    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission."""
        return self.is_admin
    
    def has_module_perms(self, app_label):
        """Check if user has permissions to view the app."""
        return True
    
    @property
    def is_staff(self):
        """Check if user is a staff member."""
        return self.is_admin
