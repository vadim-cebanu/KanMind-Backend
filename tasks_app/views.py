from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Task, Comment
from .serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer


class TaskCreateView(APIView):
    """
    POST /api/tasks/
    Creates a new task on a board. The logged-in user must be a member
    (or the owner) of that board, otherwise a 403 is returned.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            board = serializer.validated_data['board']
            is_member = board.owner == request.user or board.members.filter(id=request.user.id).exists()
            if not is_member:
                return Response(
                    {'detail': 'You must be a member of this board to create a task.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH  /api/tasks/<task_id>/ - update a task (board members only)
    DELETE /api/tasks/<task_id>/ - delete a task (creator or board owner only)
    """
    queryset = Task.objects.all()
    lookup_url_kwarg = 'task_id'
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        task = self.get_object()

        is_member = task.board.owner == request.user or task.board.members.filter(id=request.user.id).exists()
        if not is_member:
            return Response(
                {'detail': 'You must be a member of this board to update this task.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()

        if task.creator != request.user and task.board.owner != request.user:
            return Response(
                {'detail': 'Only the creator of the task or the board owner can delete it.'},
                status=status.HTTP_403_FORBIDDEN
            )
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TasksAssignedToMeView(generics.ListAPIView):
    """
    GET /api/tasks/assigned-to-me/
    Returns every task where the logged-in user is the assignee.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class TasksReviewingView(generics.ListAPIView):
    """
    GET /api/tasks/reviewing/
    Returns every task where the logged-in user is the reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class CommentListCreateView(APIView):
    """
    GET  /api/tasks/<task_id>/comments/  - list all comments on a task
    POST /api/tasks/<task_id>/comments/  - add a new comment
    Only members (or the owner) of the task's board are allowed.
    """
    permission_classes = [IsAuthenticated]

    def get_task_or_403(self, request, task_id):
        """
        Shared lookup used by both get() and post().
        Returns (task, None) on success, or (None, error_response) on failure.
        """
        task = get_object_or_404(Task, id=task_id)
        is_member = task.board.owner == request.user or task.board.members.filter(id=request.user.id).exists()
        if not is_member:
            return None, Response(
                {'detail': 'You must be a member of this board to access its comments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return task, None

    def get(self, request, task_id):
        task, error = self.get_task_or_403(request, task_id)
        if error:
            return error
        comments = task.comments.all()
        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        task, error = self.get_task_or_403(request, task_id)
        if error:
            return error

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(task=task, author=request.user)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDeleteView(APIView):
    """
    DELETE /api/tasks/<task_id>/comments/<comment_id>/
    Only the author of the comment can delete it.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, task_id=task_id)

        if comment.author != request.user:
            return Response(
                {'detail': 'Only the author of the comment can delete it.'},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)