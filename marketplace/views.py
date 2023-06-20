from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404 , render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import  DjangoModelPermissions, IsAuthenticated , AllowAny, IsAdminUser

from marketplace.permissions import IsAdminOrReadOnly 
from marketplace.models import Category, Favorite, Item, Profil
from marketplace.serializers import AddItemSerializer, AddItemToFavSerializer, CategorySerializer, FavoriteItemsSerializer, ItemSerializer, ProfilSerializer, UpdateItemSerializer

# Create your views here.

class ProfilViewSet(ModelViewSet):
    queryset = Profil.objects.select_related('user').all()
    serializer_class = ProfilSerializer

    @action(detail=False, methods=['GET', 'PATCH'], permission_classes = [IsAuthenticated])
    def me(self, request):
        profil = Profil.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = ProfilSerializer(profil)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = ProfilSerializer(profil, data = request.data)
            user = request.user
            user.first_name = request.data['first_name']
            user.last_name = request.data['last_name']
            user.save()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(products_count=Count('items')).all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


    def destroy(self, request, *args, **kwargs):
        category = get_object_or_404(Category, pk = kwargs['pk']) 
        if category.items.count() > 0:
            return Response({'error': 'Category connot be deleted because it is associated with an item.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)



    
class FavoriteViewSet(ModelViewSet):

    @action(detail=False, methods=['GET', 'PUT'], permission_classes = [IsAuthenticated])
    def get_queryset(self):
        current_user = self.request.user
        return Favorite.objects.select_related('item__category', 'item__seller__user')\
                        .filter(customer__user=current_user).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddItemToFavSerializer
        else:
            return FavoriteItemsSerializer
        
    # def get_serializer_context(self):
    #     return {'profil_id': self.kwargs['profil_pk']}
    
class ItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    queryset = Item.objects.select_related('seller__user','category').all()

    def get_serializer_class(self):
        cuurent_user = self.request.user
        if self.request.method == 'POST':
            return AddItemSerializer
        elif self.request.method == 'PATCH':
            # item = Item.objects.get(id = self.kwargs['pk'])
            # if item.seller.user == cuurent_user:
            return UpdateItemSerializer
            #return AddItemToFavSerializer
        return ItemSerializer
    
class MyOffersViewSet(ModelViewSet):

    def get_queryset(self):
        return  Item.objects.select_related('seller__user','category')\
                            .filter(seller__user = self.request.user).all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddItemSerializer
        return ItemSerializer

    


