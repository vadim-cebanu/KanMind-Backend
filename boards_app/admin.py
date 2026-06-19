from django.contrib import admin
from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin interface for Board model.
    """
    list_display = ('title', 'owner', 'created_at', 'updated_at', 'member_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'owner__email', 'owner__fullname')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Board Information', {
            'fields': ('title', 'owner')
        }),
        ('Members', {
            'fields': ('members',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('members',)
    
    def member_count(self, obj):
        """Display the number of members in the board."""
        return obj.members.count()
    member_count.short_description = 'Members'
