from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from ..models import Profil


@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_profil(sender, **kwargs):
    if kwargs['created']:
        Profil.objects.create(user = kwargs['instance'])
