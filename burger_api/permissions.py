from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_superuser
        

class IsAllowedToOrder(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (request.method == 'GET' and obj.owner == request.user) or (request.method == 'POST') or (request.user.is_superuser):
            return True
