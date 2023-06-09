from django.urls import path
from rest_framework_nested import routers
from . import views
from pprint import pprint


router = routers.DefaultRouter()
router.register('items',views.ItemViewSet, basename='items')
router.register('categories',views.CategoryViewSet)
router.register('profils',views.ProfilViewSet)


products_router =  routers.NestedDefaultRouter(router, 'items', lookup='item')


urlpatterns = router.urls + products_router.urls
