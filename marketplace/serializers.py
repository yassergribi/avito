from rest_framework import serializers
from django.conf import settings
from django.db import transaction
from core.serializers import UserSerializer
from core.models import User
from .models import Category, Favorite, Item, Profil


class ProfilSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    birth_date = serializers.DateField(required=False)
    phone = serializers.CharField()
    created_at = serializers.DateTimeField(read_only = True)
    last_update = serializers.DateTimeField(read_only = True)

    class Meta:
        model = Profil
        fields = ['id','user','phone','birth_date','created_at','last_update']


    def create(self, validated_data):
        with transaction.atomic():
            user_data = validated_data.pop('user')
            if User.objects.filter(email=user_data['email']).exists():
                    raise serializers.ValidationError("User with this email already exists.")
            
            if User.objects.filter(username=user_data['username']).exists():
                    raise serializers.ValidationError("User with this username already exists.")
                
            user = User.objects.create(**user_data)
            self.instance = Profil.objects.get(user=user) 
        return super().update(self.instance, validated_data)
        
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = self.fields['user']
            user_instance = instance.user
            if 'email' in user_data and user_data['email'] != user_instance.email:
                if User.objects.filter(email=user_data['email']).exists():
                    raise serializers.ValidationError("User with this email already exists.")
                user_instance.email = user_data['email']
                user_instance.save()
            user_instance = user_serializer.update(user_instance, user_data)
        return super().update(instance, validated_data)

    
class SimpleProfilSerializer(serializers.ModelSerializer):
    user = user = UserSerializer()
    class Meta:
        model = Profil
        fields = ['id','user','phone']

    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = self.fields['user']
            user_instance = instance.user
            if 'email' in user_data and user_data['email'] != user_instance.email:
                if User.objects.filter(email=user_data['email']).exists():
                    raise serializers.ValidationError("User with this email already exists.")
                user_instance.email = user_data['email']
                user_instance.save()
            user_instance = user_serializer.update(user_instance, user_data)
        return super().update(instance, validated_data)

    
class SellerSerializer(serializers.ModelSerializer):
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
    seller = SellerSerializer(read_only= True)
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


