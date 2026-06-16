from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Board
from .serializers import BoardSerializer, BoardDetailSerializer

class BoardListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/boards/ - Lists all boards where the logged-in user is either owner or member.
    POST /api/boards/ - Creates a new board and automatically sets the logged-in user as owner.
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]  # Protects the endpoint, requires token

    def get_queryset(self):
        """
        Filters the boards so a user can only see the boards they own 
        or the boards where they are registered as a member.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """
        Intercepts the save process to inject the logged-in user as the board owner.
        """
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/boards/<id>/ - Get details of a specific board with members and tasks.
    PUT    /api/boards/<id>/ - Update board details (title, members).
    DELETE /api/boards/<id>/ - Delete the board.
    """
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensures users can only modify or view boards they have access to.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
