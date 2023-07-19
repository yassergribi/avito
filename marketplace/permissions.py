from dis import dis
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .models import Discussion

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

class IsTextOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        elif request.method in ['GET','POST','DELETE'] :
            discussion_id = view.kwargs.get('discussion_pk')
            sender = request.user.profil
            try:
                Discussion.objects.filter(id = discussion_id).get(Q(receiver=sender) | Q(sender=sender))
            except Discussion.DoesNotExist:
                return False
        return True

class IsDiscussionOwner(permissions.BasePermission):
    def get_object_or_none(self, request, view):
        try:
            return view.get_object()
        except ObjectDoesNotExist:
            return None

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        try:
            obj = view.get_object()
        except:
            obj = None

        if obj is not None and request.method in ['GET','POST']:
            discussion_id = view.kwargs.get('pk')
            sender = request.user.profil
            try:
                Discussion.objects.get(Q(id = discussion_id) & Q(receiver=sender) | Q(id = discussion_id) & Q(sender=sender))
                return True
            except Discussion.DoesNotExist:
                return False
        elif obj is None and request.method in ['GET','POST']:
            return True

            
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