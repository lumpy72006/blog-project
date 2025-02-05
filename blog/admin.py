from django.contrib import admin
from .models import Post, Category
from .forms import PostForm

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']  
    search_fields = ['name']  
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'pub_date', 'views_count', 'tag_list']
    search_fields = ['title', 'content']
    list_filter = ['status', 'pub_date', 'category']
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('views_count','reading_time', 'likes', 'liked_by')
    autocomplete_fields = ('tags',)
    list_editable = ['status'] # allow changing status from list view

    def tag_list(self, obj):
        return ", ".join(obj.tags.names())

