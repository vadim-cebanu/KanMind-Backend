from django.db import models
from django.conf import settings


class Task(models.Model):
    """
    Represents a single task (card) inside a Kanban board.
    """

    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    # Using the 'app_label.Model' string instead of a direct import keeps
    # this app independent from the exact import path of the boards app.
    # Replace 'boards_app' below if your boards app is named differently.
    board = models.ForeignKey(
        'boards_app.Board',
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Person currently working on the task
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    # Person responsible for reviewing the task
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_to_review'
    )

    # Person who created the task. Required to enforce the "only the
    # creator or the board owner can delete this task" rule from the
    # API spec. This field is never exposed in the API response.
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']

    def __str__(self):
        """Return string representation of task (title)."""
        return self.title


class Comment(models.Model):
    """
    A single comment left on a task.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']  # comments are listed chronologically

    def __str__(self):
        """Return string representation of comment."""
        return f'Comment by {self.author} on {self.task}'