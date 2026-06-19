from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for custom User model.
    """
    list_display = ('email', 'fullname', 'is_verified', 'is_active', 'is_admin', 'created_at')
    list_filter = ('is_verified', 'is_active', 'is_admin', 'created_at')
    search_fields = ('email', 'fullname')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('fullname',)}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_verified')}),
        ('Important Dates', {'fields': ('created_at', 'updated_at', 'last_login')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2', 'is_active', 'is_admin'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    filter_horizontal = ()
