from marketplace.models import Profil
from marketplace.serializers import CreateProfilSerializer
from django.conf import settings
from rest_framework import status
from core.models import User

from model_bakery import baker
#from rest_framework.test import APIClient
import pytest


@pytest.fixture
def create_profil(api_client):
    def do_create_profil(profil):
        return api_client.post('/marketplace/createprofil/', profil, format='json')
    return do_create_profil

@pytest.fixture
def delete_profil(api_client):
    def do_delete_profil(profil):
        return api_client.delete(f'/marketplace/adminprofils/{profil.id}/')
    return do_delete_profil

@pytest.fixture
def delete_profil_me(api_client):
    def do_delete_profil_me(profil):
        return api_client.delete(f'/marketplace/adminprofils/me/')
    return do_delete_profil_me

@pytest.fixture
def patch_profil(api_client):
    def do_patch_profil(profil, values):
        return api_client.patch(f'/marketplace/adminprofils/{profil.id}/', values, format='json')
    return do_patch_profil

@pytest.fixture
def patch_profil_me(api_client):
    def do_patch_profil_me(profil, values):
        return api_client.patch(f'/marketplace/adminprofils/me/', values, format='json')
    return do_patch_profil_me


@pytest.mark.django_db
class TestRetrieveProfils:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        #arrange
        
        #act
        response = api_client.get(f'/marketplace/adminprofils/')
        #assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, api_client):
        #arrange
        authenticate()
        #act
        response = api_client.get(f'/marketplace/adminprofils/')
        #assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_profil_does_not_exists_returns_404(self,authenticate ,api_client):
        authenticate(is_staff = True)
        response = api_client.get(f'/marketplace/adminprofils/{-1}/')
        #assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    
    def test_if_adminprofil_me_returns_200(self, api_client):
        current_user = baker.make(settings.AUTH_USER_MODEL)
        
        api_client.force_authenticate(current_user)
        
        response = api_client.get(f'/marketplace/profils/me/')
        #assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == current_user.profil.id
        assert response.data['user']['username'] == current_user.username

@pytest.mark.django_db
class TestDeleteProfil:
    def test_if_user_is_admin_returns_204(self,authenticate ,delete_profil):
        authenticate(is_staff =True)

        user = baker.make(settings.AUTH_USER_MODEL)
        profil = Profil.objects.get(user=user)

        response = delete_profil(profil)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Profil.objects.count() == 0
    
    def test_if_profil_me_and_is_Authenticated_returns_204(self, api_client,delete_profil_me ):
        current_user = baker.make(settings.AUTH_USER_MODEL , is_staff=True)
        profil = Profil.objects.get(user=current_user)
        
        api_client.force_authenticate(current_user)
        
        response = delete_profil_me(profil)
        #assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
class TestUpdateProfil: 
    def test_if_user_is_anonymous_returns_401(self, patch_profil):
        user = baker.make(settings.AUTH_USER_MODEL)
        profil = Profil.objects.get(user=user)

        data = {
                    "user": {
                            "username": "testcreateprofil",
                            "email": "abc@domain.com",
                            "first_name": "first",
                            "last_name": "last",
                             },
                    "phone": "12345678"
                }
    
        response = patch_profil(profil, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self,authenticate ,patch_profil):
        authenticate()

        user = baker.make(settings.AUTH_USER_MODEL)
        profil = Profil.objects.get(user=user)

        data = {
                    "user": {
                            "username": "testcreateprofil",
                            "email": "abc@domain.com",
                            "first_name": "first",
                            "last_name": "last",
                             },
                    "phone": "12345678"
                }
    
        response = patch_profil(profil, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
    

    def test_if_user_is_admin_invalid_data_returns_400(self,api_client ,patch_profil):
        current_user = baker.make(settings.AUTH_USER_MODEL, is_staff=True)
        profil = Profil.objects.get(user=current_user)

        api_client.force_authenticate(current_user)

        data = {
                    "user": {
                            "username": "",
                            "email": "abc@domain.com",
                            "first_name": "first",
                            "last_name": "last",
                             },
                    "phone": "12345678"
                }
    
        response = patch_profil(profil, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['user']['username'] is not None

    def test_if_user_is_admin_returns_200(self,authenticate ,patch_profil):
        authenticate(is_staff=True)

        user = baker.make(settings.AUTH_USER_MODEL)
        profil = Profil.objects.get(user=user)

        data = {
                    "user": {
                            "username": "testcreateprofil",
                            "email": "abc@domain.com",
                            "first_name": "first",
                            "last_name": "last",
                             },
                    "phone": "12345678"
                }
    
        response = patch_profil(profil, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == "testcreateprofil"
        assert response.data['user']['email'] == "abc@domain.com"
        assert response.data['phone'] == "12345678"
            

@pytest.mark.django_db
class TestUpdateMeProfil: 
    def test_if_user_is_anonymous_returns_401(self, patch_profil_me):
        user = baker.make(settings.AUTH_USER_MODEL)
        profil = Profil.objects.get(user=user)

        data = {
                    "user": {
                            "username": "testcreateprofil",
                            "email": "abc@domain.com",
                            "first_name": "first",
                            "last_name": "last",
                             },
                    "phone": "12345678"
                }
    
        response = patch_profil_me(profil, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_amdin_returns_403(self,api_client ,patch_profil_me):
        current_user = baker.make(settings.AUTH_USER_MODEL)
        profil = Profil.objects.get(user=current_user)

        api_client.force_authenticate(current_user)

        data = {
                    "user": {
                            "username": "testcreateprofil",
                            "email": "abc@domain.com",
                            "first_name": "first",
                            "last_name": "last",
                             },
                    "phone": "12345678"
                }
    
        response = patch_profil_me(profil, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_user_is_owner_returns_200(self,api_client ,patch_profil_me):
        current_user = baker.make(settings.AUTH_USER_MODEL, is_staff=True)
        profil = Profil.objects.get(user=current_user)

        api_client.force_authenticate(current_user)

        data = {
                    "user": {
                            "username": "testcreateprofil",
                            "email": "abc@domain.com",
                            "first_name": "first",
                            "last_name": "last",
                             },
                    "phone": "12345678"
                }
    
        response = patch_profil_me(profil, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == profil.id
        assert response.data['user']['username'] == "testcreateprofil"
        assert response.data['user']['email'] == "abc@domain.com"
        assert response.data['phone'] == "12345678"


