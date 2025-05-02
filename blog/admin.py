from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "pub_date", "views_count"]
    search_fields = ["title", "content"]
    list_filter = ["status", "pub_date"]
    prepopulated_fields = {"slug": ("title",)}
    exclude = ("views_count", "reading_time", "likes", "liked_by")
    list_editable = ["status"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "created_date", "approved"]
    search_fields = ["post__title", "author__username", "content"]
    list_filter = ["approved", "created_date"]
    list_editable = ["approved"]
