from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
  username = models.CharField(max_length=255, unique = True)
  email = models.EmailField(unique=True)
  
