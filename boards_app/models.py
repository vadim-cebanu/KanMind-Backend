from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_boards')
    members = models.ManyToManyField(User, related_name='member_boards', blank=True)

