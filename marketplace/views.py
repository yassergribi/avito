from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404 , render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ViewSet
from rest_framework.permissions import  DjangoModelPermissions, IsAuthenticated , IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser

from .filters import ItemFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, IsAdminOrOwnerOrReadOnly, IsAdminOrOwner
from .models import Category, Favorite, Item, Profil
from .serializers import AddItemSerializer, SimpleProfilSerializer, CreateProfilSerializer ,AddItemToFavSerializer ,CategorySerializer, FavoriteItemsSerializer, ItemSerializer, ProfilSerializer, UpdateItemSerializer

# Create your views here.


class CreateProfilViewSet(ViewSet):
    serializer_class = CreateProfilSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AdminProfilViewSet(ModelViewSet):
    http_method_names = ['get','patch', 'delete']
    queryset = Profil.objects.select_related('user').all()
    serializer_class = ProfilSerializer
    permission_classes = [IsAdminUser]
    

    @action(detail=False, methods=['GET', 'PATCH', 'DELETE'], permission_classes = [IsAdminUser])
    def me(self, request):
        #current_user = request.user
        profil = Profil.objects.get(user= request.user)
        if request.method == 'GET':
            serializer = ProfilSerializer(profil)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = ProfilSerializer(profil, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            return Response({}, status.HTTP_204_NO_CONTENT)


class ProfilViewSet(ModelViewSet):
    http_method_names = ['get','patch', 'delete']
    queryset = Profil.objects.select_related('user').all()
    serializer_class = SimpleProfilSerializer
    permission_classes = [IsAdminOrOwner]


    @action(detail=False, methods=['GET','PATCH', 'DELETE'], permission_classes = [IsAuthenticated])
    def me(self, request):
        #current_user = request.user
        profil = Profil.objects.get(user= request.user)
        if request.method == 'GET':
            serializer = ProfilSerializer(profil)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = ProfilSerializer(profil, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            return Response({}, status.HTTP_204_NO_CONTENT)


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
    http_method_names = ['get','post', 'delete']
    permission_classes = [IsAuthenticated]
    
    

    @action(detail=False, methods=['GET'])
    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_staff and self.kwargs['profil_pk'] != 'me':
            return Favorite.objects.select_related('item__category', 'item__seller__user')\
                                   .filter(customer= self.kwargs['profil_pk']).all()
        else:
            return Favorite.objects.select_related('item__category', 'item__seller__user')\
                                   .filter(customer__user= current_user).all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FavoriteItemsSerializer 
        else:
            return AddItemToFavSerializer

    # def get_serializer_context(self):
    #     return {'profil_id': self.kwargs['profil_pk']}

class ItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ItemFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    queryset = Item.objects.select_related('seller__user','category').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateItemSerializer
        return ItemSerializer

class OffersViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return  Item.objects.select_related('seller__user','category')\
                            .filter(seller__user = self.request.user).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddItemSerializer
        return ItemSerializer




