from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'is_admin', False))


class IsManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'is_manager', False))


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'is_employee', False))


class AdminOrManagerCanList(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_manager', False)))


class AdminCanViewAllOrManagerCanViewEmployee(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_manager', False)))

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Unsafe methods (modify/delete) allowed only for Admin
        if request.method not in SAFE_METHODS:
            return getattr(user, 'is_admin', False)

        # Safe methods (read)
        if getattr(user, 'is_admin', False):
            return True
        if getattr(user, 'is_manager', False):
            # Managers can read employees only
            return getattr(obj, 'is_employee', False)
        return False


class IsSelfOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user

