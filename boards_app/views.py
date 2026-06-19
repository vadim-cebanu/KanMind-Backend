from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Board
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    BoardUpdateResponseSerializer,
    EmailCheckSerializer,
)

User = get_user_model()


class BoardListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/boards/ - List all boards where user is owner or member
    POST /api/boards/ - Create a new board
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return boards where the current user is either owner or member.
        
        Returns:
            QuerySet of Board objects filtered for current user
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """
        Create a new board with the current user as owner.
        
        Args:
            serializer: BoardSerializer instance with validated data
        """
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/boards/<id>/ - Retrieve board details (owner/members only)
    PATCH  /api/boards/<id>/ - Update board (owner/members only)
    DELETE /api/boards/<id>/ - Delete board (owner only)
    """
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get board and enforce permissions.
        
        Returns:
            Board instance if user has permission
            
        Raises:
            PermissionDenied: If user lacks required permissions
        """
        board = get_object_or_404(Board, pk=self.kwargs['pk'])
        user = self.request.user
        is_member = board.owner == user or board.members.filter(id=user.id).exists()

        if self.request.method == 'DELETE':
            # only the owner may delete - documented explicitly
            if board.owner != user:
                self.permission_denied(self.request, message='Only the board owner can delete this board.')
        else:
            # GET / PATCH: owner or member
            if not is_member:
                self.permission_denied(self.request, message='You must be a member of this board.')

        return board

    def get_serializer_class(self):
        """
        Return appropriate serializer based on HTTP method.
        
        Returns:
            BoardUpdateSerializer for PATCH requests
            BoardDetailSerializer for other requests
        """
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def update(self, request, *args, **kwargs):
        """
        Handle board update requests.
        
        Args:
            request: HTTP request with board update data
            
        Returns:
            Response with updated board data (200)
            Response with validation errors (400)
        """
        board = self.get_object()

        input_serializer = BoardUpdateSerializer(board, data=request.data, partial=True)
        if input_serializer.is_valid():
            board = input_serializer.save()
            # the PATCH response uses a different shape (owner_data /
            # members_data) than the GET response - see BoardUpdateResponseSerializer
            output_serializer = BoardUpdateResponseSerializer(board)
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailCheckView(APIView):
    """
    GET /api/email-check/?email=<email> - Check if user exists by email
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Check if a user exists with the given email.
        
        Args:
            request: HTTP request with 'email' query parameter
            
        Returns:
            Response with user data if found (200)
            Response with error if not found (404)
            Response with validation errors (400)
        """
        serializer = EmailCheckSerializer(data=request.query_params)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'No user found with this email.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {'id': user.id, 'email': user.email, 'fullname': user.fullname},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)