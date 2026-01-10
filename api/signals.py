from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from blog.models import Post

@receiver([post_save, post_delete], sender=Post)
def invalidate_post_cache(sender, instance, **kwargs):
    """
    Invalidate cache when a post is modified
    """
    cache.delete(f"post_detail_{instance.slug}") # specific post
    cache.delete_pattern("*post_list*")
