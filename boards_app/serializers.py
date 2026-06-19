from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Board
from tasks_app.serializers import TaskSerializer
from tasks_app.serializers import UserSimpleSerializer


User = get_user_model()


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for board detail view (GET /api/boards/<id>/).
    Returns board with owner_id, members list, and all tasks.
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
    Serializer for board list and creation.
    Used for GET /api/boards/ and POST /api/boards/.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField(source='owner.id')

    # write_only=True: accepted on input (POST), but never included in the
    # output - the documented GET/POST response only has 'member_count',
    # never a raw list of member IDs.
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count',
                  'tasks_high_prio_count', 'owner_id', 'members']
        read_only_fields = ['owner_id']

    def get_member_count(self, obj):
        """Returns the number of members in this board"""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Returns the total number of tickets/tasks in this board"""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Returns the number of tasks with 'to-do' status"""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Returns the number of high priority tasks"""
        return obj.tasks.filter(priority='high').count()

    def create(self, validated_data):
        """
        Create a new board with members.
        
        Args:
            validated_data: Dictionary of validated board data
            
        Returns:
            Newly created Board instance with members added
        """
        members = validated_data.pop('members', [])
        # the owner is added to members automatically inside Board.save()
        board = Board.objects.create(**validated_data)
        if members:
            # IMPORTANT: use add(), not set().
            # set() would REPLACE the whole members list, wiping out the
            # owner that Board.save() just added, unless the owner's own
            # id happens to be included in the submitted list.
            board.members.add(*members)
        return board


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Input serializer for PATCH /api/boards/<id>/.
    Allows updating title and replacing the members list.
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    def update(self, instance, validated_data):
        """
        Update board title and/or members list.
        
        Args:
            instance: Board instance to update
            validated_data: Dictionary of validated update data
            
        Returns:
            Updated Board instance
        """
        members = validated_data.pop('members', None)
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        if members is not None:
            # set() is correct here: PATCH is meant to REPLACE the member
            # list with exactly the one sent by the client.
            instance.members.set(members)
        return instance


class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    """
    Output serializer for PATCH /api/boards/<id>/ response.
    Returns board with owner_data and members_data as nested objects.
    """
    owner_data = UserSimpleSerializer(source='owner', read_only=True)
    members_data = UserSimpleSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']


class EmailCheckSerializer(serializers.Serializer):
    """
    Serializer for email validation in GET /api/email-check/.
    """
    email = serializers.EmailField()