from django.contrib import admin
from .models import Task, Comment


class CommentInline(admin.TabularInline):
    """
    Inline admin for Comments on Task detail page.
    """
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('author', 'content', 'created_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for Task model.
    """
    list_display = ('title', 'board', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'created_at', 'due_date', 'board')
    search_fields = ('title', 'description', 'board__title', 'assignee__email', 'creator__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Task Information', {
            'fields': ('board', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assignee', 'reviewer', 'creator')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CommentInline]
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys."""
        return super().get_queryset(request).select_related(
            'board', 'assignee', 'reviewer', 'creator'
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model.
    """
    list_display = ('task', 'author', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'task__title', 'author__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('task', 'author', 'content')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        """Display a preview of the comment content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys."""
        return super().get_queryset(request).select_related('task', 'author')
