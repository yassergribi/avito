from djoser.serializers import UserSerializer as BaseUserSerializer , UserCreateSerializer as BaseUserCreateSerializer
from marketplace import serializers
from rest_framework import serializers as drfserializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id',"username", "password", "email", "first_name", "last_name"]
        
class UserSerializer(BaseUserSerializer):
    username = drfserializers.CharField()
    email = drfserializers.EmailField()
    class Meta(BaseUserSerializer.Meta):
        fields = ['id',"username", "email", "first_name", "last_name"]