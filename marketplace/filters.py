from dataclasses import fields
from django_filters.rest_framework import FilterSet
from .models import Item

class ItemFilter(FilterSet):
    class Meta:
        model = Item
        fields = {
            'category_id' : ['exact'],
            'price' : ['gt', 'lt']
        }
