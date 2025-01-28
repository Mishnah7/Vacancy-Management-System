from django import template

from jobsapp.models import Favorite

register = template.Library()


@register.filter(name='is_favorited')
def is_favorited(job, user):
    """
    Check if a job is favorited by a user
    Usage: {{ job|is_favorited:user }}
    """
    if not user.is_authenticated:
        return False
    return Favorite.objects.filter(job=job, user=user).exists()
