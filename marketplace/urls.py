from django.urls import path
from rest_framework_nested import routers
from . import views
from pprint import pprint


router = routers.DefaultRouter()
router.register('items',views.ItemViewSet, basename='items')
router.register('categories',views.CategoryViewSet)
router.register('profils',views.ProfilViewSet, basename='profils')
router.register('adminprofils', views.AdminProfilViewSet, basename='adminprofils')
router.register('createprofil', views.CreateProfilViewSet, basename='createprofil')


items_router =  routers.NestedDefaultRouter(router, 'items', lookup='item')

profils_router =  routers.NestedDefaultRouter(router, 'profils', lookup='profil')
profils_router.register('favorites',views.FavoriteViewSet, basename='profil-favorites' )
profils_router.register('myoffers',views.MyOffersViewSet, basename='profil-myoffers' )


urlpatterns = router.urls + items_router.urls + profils_router.urls
