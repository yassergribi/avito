from django.contrib import admin

from . import models

# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_display = ['title','price','seller','category_name','last_update']
    search_fields = ['title']
    prepopulated_fields = {'slug' : ['title']}
    list_per_page = 10
    #list_select_related = ['category']


    def category_name(self, item):
        return item.category.title


admin.site.register(models.Item , ItemAdmin)