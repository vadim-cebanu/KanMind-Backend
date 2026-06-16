from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Board
from tasks_app.models import Task

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested representations"""
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id', 'email', 'fullname']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with nested user info"""
    assignee = UserSimpleSerializer(read_only=True)
    reviewer = UserSimpleSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 
                  'assignee', 'reviewer', 'due_date', 'comments_count']
        read_only_fields = ['id', 'comments_count']
    
    def get_comments_count(self, obj):
        """Returns the number of comments on this task"""
        # TODO: Implement when Comment model is created
        return 0


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Board detail view.
    Returns full board info with members and tasks.
    """
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = UserSimpleSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'owner_id']


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for Board list view.
    Returns board summary with counts for members, tickets, and tasks.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 
                  'tasks_high_prio_count', 'owner_id']
        read_only_fields = ['owner_id']

    def get_member_count(self, obj):
        """Returns the number of members in this board"""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Returns the total number of tickets/tasks in this board"""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Returns the number of tasks with 'to do' status"""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Returns the number of high priority tasks"""
        return obj.tasks.filter(priority='high').count()
