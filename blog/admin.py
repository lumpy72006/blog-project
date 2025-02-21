from django.contrib import admin
from .models import Post
from .forms import PostForm


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "pub_date", "views_count", "tag_list"]
    search_fields = ["title", "content"]
    list_filter = ["status", "pub_date"]
    prepopulated_fields = {"slug": ("title",)}
    exclude = ("views_count", "reading_time", "likes", "liked_by")
    autocomplete_fields = ("tags",)
    list_editable = ["status"]  # allow changing status from list view

    def tag_list(self, obj):
        return ", ".join(obj.tags.names())
