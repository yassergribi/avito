from marketplace.models import Category, Item
from django.conf import settings
from rest_framework import status
from model_bakery import baker

import pytest


@pytest.fixture
def create_category(api_client):
    def do_create_category(category):
        return api_client.post('/marketplace/categories/', category)
    return do_create_category

@pytest.fixture
def delete_category(api_client):
    def do_delete_category(category):
        return api_client.delete(f'/marketplace/categories/{category.id}/')
    return do_delete_category

@pytest.fixture
def patch_category(api_client):
    def do_patch_category(category, value):
        return api_client.patch(f'/marketplace/categories/{category.id}/', value) 
    return do_patch_category

@pytest.mark.django_db
class TestCreateCategory:
    def test_if_user_is_anonymous_returns_401(self, create_category):
        response = create_category({'title' : 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, authenticate, create_category):
        authenticate()

        response = create_category({'title' : 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self, authenticate, create_category):
        authenticate(is_staff = True ) 

        response = create_category({'title' : ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, create_category):
        authenticate(is_staff = True) 

        response = create_category({'title' : 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

@pytest.mark.django_db
class TestRetrieveCategory:
    def test_if_category_exists_returns_200(self, api_client):
        #arrange
        category = baker.make(Category)
        #act
        response = api_client.get(f'/marketplace/categories/{category.id}/')
        #assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id
        assert response.data['title'] == category.title
    
    def test_if_category_does_not_exists_returns_404(self, api_client):
        response = api_client.get(f'/marketplace/categories/{-1}/')
        #assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteCategory:
    def test_if_user_is_anonymous_returns_401(self, delete_category):
        #arrange 
        category = baker.make(Category)
        #act
        response = delete_category(category)
        #assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate ,delete_category):
        authenticate()
        category = baker.make(Category)

        response = delete_category(category)

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_category_is_not_found_returns_404(self, authenticate, delete_category):
        authenticate(is_staff= True)

        response = delete_category(Category)

        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_if_user_is_admin_and_deleted_returns_204(self, authenticate, delete_category):
        authenticate(is_staff= True)
        category = baker.make(Category)

        response = delete_category(category)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        response = delete_category(category)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_category_is_not_empty_returns_405(self, authenticate, delete_category):
        authenticate(is_staff= True)
        category = baker.make(Category)
        user = baker.make(settings.AUTH_USER_MODEL)
        item = baker.make(Item,seller=user.profil ,category=category)

        assert category.items.count() > 0 
        response = delete_category(category)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db       
class TestUpdateCollection:
    def test_if_user_is_anonymous_returns_401(self, patch_category):
        category = baker.make(Category)

        response = patch_category(category, {'title' : 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self,authenticate,patch_category):
        authenticate()
        category = baker.make(Category)

        response = patch_category(category, {'title' : 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self,authenticate, patch_category):
        authenticate(is_staff = True)
        category = baker.make(Category)

        response = patch_category(category, {'title' : ''})

        assert response.data['title'] is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_user_is_admin_and_data_is_valid_returns_200(self,authenticate, patch_category):
        authenticate(is_staff = True)
        category = baker.make(Category)

        response = patch_category(category, {'title' : 'S'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id
        assert response.data['title'] == 'S'
        