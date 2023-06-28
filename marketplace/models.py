from django.conf import settings 
from django.db import models
from django.core.validators import MinValueValidator , FileExtensionValidator


from .validators import validate_file_size
# Create your models here.


class Profil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'profil')
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Category(models.Model):
    title = models.CharField(max_length=255)
    featured_items = models.ForeignKey('Item', on_delete = models.SET_NULL, null=True, related_name = '+')
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class Item(models.Model):
    title = models.CharField(max_length= 255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank = True)
    price = models.DecimalField(
            max_digits=8 , 
            decimal_places = 2,
            validators = [MinValueValidator(1)])
    seller = models.ForeignKey(Profil, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Favorite(models.Model):
    customer = models.ForeignKey(Profil, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = [['customer', 'item']]

class Image(models.Model):
    item = models.ForeignKey(Item, on_delete= models.CASCADE, related_name = 'images')
    image = models.ImageField(
        upload_to='marketplace/images',
        validators=[validate_file_size])
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


class AddressItem(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    item = models.ForeignKey(Item, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    

class AddressUser(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

