from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import generics
from .api.serializers import BoardListSerializer
from .models import Board


class BoardListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset= Board.objects.all()
    serializer_class=BoardListSerializer
  

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BoardListSerializer  
    
  