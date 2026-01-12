from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from blog.models import Post

@receiver([post_save, post_delete], sender=Post)
def invalidate_post_cache(sender, instance, **kwargs):
    """
    Invalidate cache when a post is modified
    """
    # This works on all cache types
    cache.delete(f"post_detail_{instance.slug}") 

    # This check prevents the crash! 
    # It asks: "Do you know how to delete_pattern?"
    if hasattr(cache, "delete_pattern"):
        cache.delete_pattern("*post_list*")
    else:
        # Fallback for basic caches (like the one on Render right now)
        # We just clear the whole cache to be safe, or you can pass
        cache.clear()
