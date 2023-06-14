from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.conf import settings
from .models import Category, Favorite, Item, Profil


class ProfilSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    first_name = serializers.SerializerMethodField()
    last_name =  serializers.SerializerMethodField()

    class Meta:
        model = Profil
        fields = ['id', 'user_id','first_name','last_name','phone','birth_date']

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
    seller = SimpleProfilSerializer()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id','title','description','price','seller','category']

    def get_category(self, item:Item):
        return item.category.title

class AddItemSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(read_only = True)

    class Meta:
        model = Item
        fields = ['id','title','description','price','seller_id','category']

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        seller_id = Profil.objects.get(user_id=user_id).id
        return Item.objects.create(seller_id=seller_id , **validated_data)


class UpdateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['title','description','price']

class AddItemToFavSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only = True)
    class Meta:
        model = Favorite
        fields = ['id', 'user_id', 'item']

    def create(self, validated_data):
        user_id = self.context['profil_id']
        return Favorite.objects.create(user_id=user_id, **validated_data)


class FavoriteItemsSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    class Meta:
        model = Favorite
        fields = ['id','item']