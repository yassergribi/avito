from rest_framework import serializers
from .models import Category, Item, Profil


class ProfilSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profil
        fields = ['id', 'user_id', 'phone','birth_date']

class SimpleProfilSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profil
        fields = ['id','phone']
    

class CategorySerializer(serializers.ModelSerializer):
    featured_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id','title','featured_items']


class ItemSerializer(serializers.ModelSerializer):
    seller = SimpleProfilSerializer()

    class Meta:
        model = Item
        fields = ['id','title','description','price','seller','category']

class AddItemSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(read_only = True)

    class Meta:
        model = Item
        fields = ['id','title','description','price','seller_id','category']

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        seller = Profil.objects.get(user_id=user_id)
        return Item.objects.create(seller_id=seller.id , **validated_data)


class UpdateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['title','description','price']

