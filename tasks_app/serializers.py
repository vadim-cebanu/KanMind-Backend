from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task, Comment

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    """
    Minimal user representation, used wherever we need to show "who"
    without exposing sensitive fields - members, assignee, reviewer, owner.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class TaskSerializer(serializers.ModelSerializer):
    """
    Output serializer for tasks. Used inside BoardDetailSerializer,
    assigned-to-me, reviewing, and as the response after create/update.
    """
    assignee = UserSimpleSerializer(read_only=True)
    reviewer = UserSimpleSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority',
                  'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, obj):
        """
        Calculate the number of comments on this task.
        
        Args:
            obj: Task instance
            
        Returns:
            Integer count of comments
        """
        """Returns the number of comments on this task"""
        return obj.comments.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Input serializer for POST /api/tasks/.
    Accepts assignee_id / reviewer_id (plain numbers) instead of full
    nested user objects - matches the API spec request body.
    """
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee', queryset=User.objects.all(), required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer', queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = ['board', 'title', 'description', 'status', 'priority',
                  'assignee_id', 'reviewer_id', 'due_date']

    def validate(self, attrs):
        """
        Validate that assignee and reviewer are members of the board.
        
        Args:
            attrs: Dictionary of validated field data
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If assignee or reviewer is not a board member
        """
        board = attrs.get('board')
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')

        if assignee and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError({'assignee_id': 'User is not a member of this board.'})
        if reviewer and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError({'reviewer_id': 'User is not a member of this board.'})
        return attrs

    def create(self, validated_data):
        """
        Create a new task with the current user as creator.
        
        Args:
            validated_data: Dictionary of validated task data
            
        Returns:
            Newly created Task instance
        """
        creator = self.context['request'].user
        return Task.objects.create(creator=creator, **validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Input serializer for PATCH /api/tasks/<id>/.
    'board' is intentionally left out - changing the board of an
    existing task is not allowed by the API spec.
    """
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee', queryset=User.objects.all(), required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer', queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority',
                  'assignee_id', 'reviewer_id', 'due_date']

    def validate(self, attrs):
        """
        Validate that assignee and reviewer are members of the task's board.
        
        Args:
            attrs: Dictionary of validated field data
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If assignee or reviewer is not a board member
        """
        board = self.instance.board
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')

        if assignee and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError({'assignee_id': 'User is not a member of this board.'})
        if reviewer and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError({'reviewer_id': 'User is not a member of this board.'})
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """
    Output serializer for GET/POST /api/tasks/<id>/comments/.
    'author' is returned as a plain string (full name) per the API spec,
    not as a nested object. The same serializer is reused for input -
    the client only ever sends 'content', everything else is read-only.
    """
    author = serializers.CharField(source='author.fullname', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']