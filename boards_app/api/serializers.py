from rest_framework import serializers
from ..models import Board



class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    class Meta:
        model=Board
        fields=['id', 'title', 'member_count','owner_id']
    
    def get_member_count(self,obj):
        return obj.members.count()
  
  

    