from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()
router.register('items',views.ItemViewSet, basename='items')
router.register('categories',views.CategoryViewSet)
router.register('profils',views.ProfilViewSet, basename='profils')
router.register('adminprofils', views.AdminProfilViewSet, basename='adminprofils')
router.register('createprofil', views.CreateProfilViewSet, basename='createprofil')
router.register('discussions',views.DiscussionViewSet, basename='discussions')


items_router =  routers.NestedSimpleRouter(router, 'items', lookup='item')
# items_router.register('discussions',views.DiscussionViewSet, basename='item-discussions')

discussions_router = routers.NestedSimpleRouter(router, 'discussions', lookup='discussion')
discussions_router.register('messages',views.MessageViewSet, basename ='discussion-messages' )

profils_router =  routers.NestedSimpleRouter(router, 'profils', lookup='profil')
profils_router.register('favorites',views.FavoriteViewSet, basename='profil-favorites' )
profils_router.register('offers',views.OffersViewSet, basename='profil-offers' )


urlpatterns = router.urls + items_router.urls + profils_router.urls + discussions_router.urls
