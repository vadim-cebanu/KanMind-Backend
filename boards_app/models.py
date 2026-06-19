from django.db import models
from django.conf import settings


class Board(models.Model):
    """
    Represents a Kanban board owned by a user.
    The owner is automatically added to the members list when the board is created.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='boards',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'boards'
        ordering = ['-created_at']

    def __str__(self):
        """Return string representation of board (title)."""
        return self.title

    def save(self, *args, **kwargs):
        """
        Save the board and automatically add owner to members if it's a new board.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Add owner to members automatically
        if is_new:
            self.members.add(self.owner)
