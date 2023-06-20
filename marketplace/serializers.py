from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.conf import settings
from .models import Category, Favorite, Item, Profil


class ProfilSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    first_name = serializers.SerializerMethodField()
    last_name =  serializers.SerializerMethodField()
    birth_date = serializers.DateField()
    created_at = serializers.DateTimeField(read_only = True)
    last_update = serializers.DateTimeField(read_only = True)

    class Meta:
        model = Profil
        fields = ['id', 'user_id','first_name','last_name','phone','birth_date','created_at','last_update']

    def get_first_name(self, profil:Profil):
        return profil.user.first_name
    def get_last_name(self, profil:Profil):
        return profil.user.last_name


    
class SimpleProfilSerializer(serializers.ModelSerializer):
    seller_name = serializers.SerializerMethodField()

    class Meta:
        model = Profil
        fields = ['id','seller_name','phone']

    def get_seller_name(self, profil:Profil):
        return profil.user.first_name
    

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id','title','products_count']


class ItemSerializer(serializers.ModelSerializer):
    seller = SimpleProfilSerializer(read_only= True)
    category = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only = True)
    last_update = serializers.DateTimeField(read_only = True)

    class Meta:
        model = Item
        fields = ['id','title','description','price','seller','category','created_at','last_update']

    def get_category(self, item:Item):
        return item.category.title

class UpdateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['title','description','price']

class AddItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id','title','description','price','category']

    def create(self, validated_data):
        user = self.context['request'].user
        seller = Profil.objects.get(user=user)
        return Item.objects.create(seller=seller , **validated_data)
    


class FavoriteItemsSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    class Meta:
        model = Favorite
        fields = ['id','item']

class AddItemToFavSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'item']

    def validate(self, attrs):
        customer = Profil.objects.get(user = self.context['request'].user)
        if Favorite.objects.filter(item = attrs['item'], customer = customer ).exists():
            raise serializers.ValidationError('This item already exists in favorite items.')
        return super().validate(attrs)    

    def create(self, validated_data):
        current_user = self.context['request'].user
        profil = Profil.objects.get(user = current_user)
        return Favorite.objects.create(customer = profil, **validated_data)


