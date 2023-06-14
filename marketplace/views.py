from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import  DjangoModelPermissions, IsAuthenticated , AllowAny, IsAdminUser


from django.shortcuts import render
from marketplace.models import Category, Favorite, Item, Profil
from marketplace.serializers import AddItemSerializer, AddItemToFavSerializer, CategorySerializer, FavoriteItemsSerializer, ItemSerializer, ProfilSerializer, UpdateItemSerializer

# Create your views here.

class ProfilViewSet(ModelViewSet):
    queryset = Profil.objects.select_related('user').all()
    serializer_class = ProfilSerializer

    @action(detail=False, methods=['GET', 'PUT'], permission_classes = [IsAuthenticated])
    def me(self, request):
        profil = Profil.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = ProfilSerializer(profil)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = ProfilSerializer(profil, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(
            products_count=Count('items')).all()
    serializer_class = CategorySerializer

    
class FavoriteViewSet(ModelViewSet):

    #@action(detail=False, methods=['GET', 'PUT'], permission_classes = [IsAuthenticated])
    def get_queryset(self):
        user_id = self.kwargs['profil_pk']
        return Favorite.objects.select_related('item__category', 'item__seller__user').filter(user_id=user_id).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddItemToFavSerializer
        else:
            return FavoriteItemsSerializer
        
    def get_serializer_context(self):
        return {'profil_id': self.kwargs['profil_pk']}
    
class ItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    queryset = Item.objects.select_related('seller__user','category').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateItemSerializer
        return ItemSerializer
    


