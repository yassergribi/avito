from email import message
from rest_framework import serializers 
from django.contrib.auth.hashers import make_password
from django.db.models import Q , F , Func , ExpressionWrapper
from django.conf import settings
from django.db import transaction
from core.serializers import UserSerializer,UserCreateSerializer
from core.models import User
from .models import Category, Favorite, Item, Profil , Discussion, Message


class CreateProfilSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    class Meta:
        model = Profil
        fields = ['id','user','phone','birth_date']
    
    def create(self, validated_data):
        with transaction.atomic():
            user_data = validated_data.pop('user')
            if User.objects.filter(email=user_data['email']).exists():
                    raise serializers.ValidationError("User with this email already exists.")
            
            if User.objects.filter(username=user_data['username']).exists():
                    raise serializers.ValidationError("User with this username already exists.")
            
            user_instance = User.objects.create(**user_data)
            user_instance.password = make_password(user_data['password'])
            user_instance.save()
            self.instance = Profil.objects.get(user=user_instance) 
        return super().update(self.instance, validated_data)



class ProfilSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    birth_date = serializers.DateField(required=False)
    phone = serializers.CharField()
    created_at = serializers.DateTimeField(read_only = True)
    last_update = serializers.DateTimeField(read_only = True)

    class Meta:
        model = Profil
        fields = ['id','user','phone','birth_date','created_at','last_update']

        
    
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
    user =  UserSerializer()
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
        fields = ['id','title','description','price']

class AddItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id','title','description','price','category']

    def create(self, validated_data):
        user = self.context['request'].user
        return Item.objects.create(seller=user.profil , **validated_data)
    


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
        current_user = self.context['request'].user
        if Favorite.objects.filter(item = attrs['item'], customer = current_user.profil ).exists():
            raise serializers.ValidationError('This item already exists in favorite items.')
        return super().validate(attrs)    

    def create(self, validated_data):
        current_user = self.context['request'].user
        return Favorite.objects.create(customer = current_user.profil, **validated_data)

    
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id','sender','message']

    def get_sender(self, msg:Message):
        return msg.sender.user.first_name
    
    def validate(self, attrs):
        sender = self.context['user'].profil
        discussion_id = self.context['discussion_id']
            
        try:
            Discussion.objects.get(Q(id = discussion_id) & Q(receiver=sender) | Q(id = discussion_id) & Q(sender=sender))
        except Discussion.DoesNotExist:
            raise serializers.ValidationError('This message can not be sent.')
        return super().validate(attrs)     
    
    def create(self, validated_data):
        sender = self.context['user'].profil
        discussion_id = self.context['discussion_id']
        text = validated_data['message']

        message = Message.objects.create(discussion_id=discussion_id, sender=sender, message=text)

        return message
    
    

class DiscussionSerializer(serializers.ModelSerializer):
    message = MessageSerializer(many=True)
    receiver = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    class Meta:
        model = Discussion
        fields = ['id', 'receiver','sender', 'message']

    
    def get_receiver(self, discussion:Discussion):
        return discussion.receiver.user.first_name
    def get_sender(self, discussion:Discussion):
        return discussion.sender.user.first_name
                      
    

class SendMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField()
    sender = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Discussion
        fields = ['id', 'receiver','sender' ,'message']

    def get_sender(self, data):
        return self.context['user'].first_name
    

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks"""
        return []
    
  
    def create(self, validated_data):
        sender = self.context['user'].profil
        receiver = validated_data['receiver']
        text = validated_data['message']

        try :
            discussion = Discussion.objects.get(Q(receiver=receiver) & Q(sender=sender) )
            Message.objects.create(discussion=discussion, sender = sender, message=text) 
            return discussion
        except Discussion.DoesNotExist:
            discussion = Discussion.objects.create(receiver=receiver, sender=sender)
            Message.objects.create(discussion=discussion, sender = sender, message=text)   
            return discussion
