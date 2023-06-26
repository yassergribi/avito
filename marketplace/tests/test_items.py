from marketplace.models import Item, Category
from django.conf import settings
from rest_framework import status
from model_bakery import baker
#from rest_framework.test import APIClient
import pytest


@pytest.fixture
def create_item(api_client):
    def do_create_item(item):
        return api_client.post('/marketplace/items/', item)
    return do_create_item

@pytest.fixture
def delete_item(api_client):
    def do_delete_item(item):
        return api_client.delete(f'/marketplace/items/{item.id}/')
    return do_delete_item

@pytest.fixture
def patch_item(api_client):
    def do_patch_item(item, values):
        return api_client.patch(f'/marketplace/items/{item.id}/', values)
    return do_patch_item


@pytest.mark.django_db
class TestCreationItem:
    def test_if_user_is_anonymous_returns_401(self, create_item):

        category = baker.make(Category)
        user = baker.make(settings.AUTH_USER_MODEL)

        response = create_item({    "title": "a",
                                    "description": "a",
                                    "slug": "-",
                                    "seller": user.profil.id,
                                    "price": 1,
                                    "category": category.id,
                                })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_invalid_returns_400(self, api_client, create_item):
        current_user = baker.make(settings.AUTH_USER_MODEL)
        api_client.force_authenticate(current_user)
        category = baker.make(Category)

        response = create_item({    "title": "",
                                    "slug": "-",
                                    "description": "a",
                                    "price": 1,
                                    "category": category.id,
                                    "seller": current_user.profil.id,
                                })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None


    def test_if_data_is_valid_returns_201(self , api_client ,create_item):
        current_user = baker.make(settings.AUTH_USER_MODEL)
        api_client.force_authenticate(current_user)
        category = baker.make(Category)

        response = create_item({    "title": "S",
                                    "slug": "-",
                                    "description": "a",
                                    "price": 1,
                                    "category": category.id,
                                    "seller": current_user.profil.id,
                                })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
        assert response.data['title'] == "S"
        assert response.data['category'] == category.id

@pytest.mark.django_db
class TestRetrieveItem:
    def test_if_item_exists_returns_200(self, api_client):
        #arrange
        user = baker.make(settings.AUTH_USER_MODEL)
        category = baker.make(Category)
        item = baker.make(Item, seller = user.profil, category=category)

        #act
        response = api_client.get(f'/marketplace/items/{item.id}/')
        #assert
        assert response.status_code == status.HTTP_200_OK
        #item.refresh_from_db()
        assert response.data['id'] == item.id
        assert response.data['title'] == item.title
        assert response.data['price'] == item.price
        assert response.data['seller']['id'] == item.seller.id
        assert response.data['category'] == item.category.title

    def test_if_item_does_not_exist_returns_404(self, api_client):

        response = api_client.get(f'/marketplace/items/{-1}/')
        #assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteItem:
    def test_if_user_is_anonymous_returns_401(self,delete_item):
        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item, seller=user.profil)

        response = delete_item(item)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_or_owner_returns_403(self,authenticate,delete_item):
        authenticate()

        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item, seller=user.profil)

        response = delete_item(item)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_owner_returns_204(self,api_client,delete_item):
        current_user = baker.make(settings.AUTH_USER_MODEL)
        api_client.force_authenticate(current_user)

        item = baker.make(Item, seller=current_user.profil)

        response = delete_item(item)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Item.objects.all().count() == 0
    
    def test_if_user_is_admin_returns_204(self,authenticate,delete_item):
        authenticate(is_staff = True )

        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item, seller=user.profil)

        response = delete_item(item)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Item.objects.all().count() == 0
    
    def test_if_product_is_not_found_returns_404(self, authenticate, delete_item):
        authenticate(is_staff = True ) 

        response = delete_item(Item)

        assert response.status_code == status.HTTP_404_NOT_FOUND
    

@pytest.mark.django_db
class TestUpdateItem: 
    def test_if_user_is_anonymous_returns_401(self, patch_item):
        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item, seller=user.profil)
    
        response = patch_item(item, {'title' : 'S', 'price' : 11 })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_or_owner_returns_403(self, authenticate, patch_item):
        authenticate()

        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item, seller=user.profil)
    
        response = patch_item(item, {'title' : 'S', 'price' : 11 })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_and_invalid_data_returns_400(self, authenticate, patch_item):
        authenticate(is_staff =True)

        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item, seller=user.profil)
    
        response = patch_item(item, {'title' : '', 'price' : -6 })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
    
    def test_if_user_is_owner_and_invalid_data__returns_400(self, api_client, patch_item):
        current_user = baker.make(settings.AUTH_USER_MODEL)
        api_client.force_authenticate(current_user)

        item = baker.make(Item, seller=current_user.profil)
    
        response = patch_item(item, {'title' : '', 'price' : -6 })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_user_is_owner_and_data_is_valid_returns_200(self, api_client, patch_item):
        current_user = baker.make(settings.AUTH_USER_MODEL)
        api_client.force_authenticate(current_user)

        item = baker.make(Item, seller=current_user.profil)
    
        response = patch_item(item, {'title' : 'S', 'price' : 13 })

        assert response.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert response.data['id'] == item.id
        assert response.data['title'] == 'S'
        assert response.data['price'] == 13

    def test_if_user_is_admin_and_data_is_valid_returns_200(self, authenticate, patch_item):
        authenticate(is_staff =True)

        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item, seller=user.profil)
    
        response = patch_item(item, {'title' : 'S', 'price' : 13 })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == item.id
        assert response.data['title'] == 'S'
        assert response.data['price'] == 13