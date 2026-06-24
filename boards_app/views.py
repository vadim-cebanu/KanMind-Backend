# boards/views.py
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
from .permissions import IsBoardOwnerOrMember, IsBoardOwner

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
            QuerySet: Board objects filtered for current user
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

    def get_serializer_class(self):
        """
        Return appropriate serializer based on HTTP method.
        
        Returns:
            class: BoardUpdateSerializer for PATCH requests,
                   BoardDetailSerializer for other requests
        """
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def check_permissions(self, request):
        """
        Verify permissions based on HTTP method.
        
        DELETE operations require board ownership.
        GET/PATCH operations require board membership or ownership.
        
        Args:
            request: The HTTP request
            
        Raises:
            PermissionDenied: If user lacks required permissions
        """
        super().check_permissions(request)
        
        board = self.get_object()
        
        if request.method == 'DELETE':
            permission = IsBoardOwner()
            if not permission.has_object_permission(request, self, board):
                self.permission_denied(
                    request,
                    message='Only the board owner can delete this board.'
                )
        else:
            permission = IsBoardOwnerOrMember()
            if not permission.has_object_permission(request, self, board):
                self.permission_denied(
                    request,
                    message='You must be a member of this board.'
                )

    def update(self, request, *args, **kwargs):
        """
        Handle board update requests.
        
        Args:
            request: HTTP request with board update data
            
        Returns:
            Response: Updated board data (200)
                      Validation errors (400)
        """
        board = self.get_object()
        
        input_serializer = BoardUpdateSerializer(
            board,
            data=request.data,
            partial=True
        )
        if input_serializer.is_valid():
            board = input_serializer.save()
            # PATCH response uses different shape than GET response
            # See BoardUpdateResponseSerializer for details
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
        Check if a user exists with the given email address.
        
        Args:
            request: HTTP request with 'email' query parameter
            
        Returns:
            Response: User data (id, email, fullname) if found (200)
                      Error message if not found (404)
                      Validation errors (400)
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
                {
                    'id': user.id,
                    'email': user.email,
                    'fullname': user.fullname
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)