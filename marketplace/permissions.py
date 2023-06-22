from rest_framework import permissions 

class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is an admin or the original user or read only
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        elif request.method in  ['PATCH','DELETE'] :
            return bool(request.user.is_authenticated and (request.user.is_staff or view.get_object().seller.user == request.user))

class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is an admin or the original user or read only
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method in  ['PATCH','DELETE'] :
            return bool(request.user.is_authenticated and (request.user.is_staff or view.get_object().user == request.user))
        
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
    
class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

class ViewCustomerHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')