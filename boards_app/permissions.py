from rest_framework.permissions import BasePermission


class IsBoardOwnerOrMember(BasePermission):
    """
    Permission class to check if user is the owner or a member of the board.
    
    Allows access if the requesting user is either the board owner or
    is listed in the board's members.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the board object.
        
        """
        user = request.user
        is_member = obj.owner == user or obj.members.filter(id=user.id).exists()
        return is_member


class IsBoardOwner(BasePermission):
    """
    Permission class to check if user is the owner of the board.
    
    Restricts access to only the board owner. Used for destructive
    operations like DELETE.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the board owner.
       
        """
        return obj.owner == request.user