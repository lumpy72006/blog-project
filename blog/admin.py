from django.contrib import admin
from .models import Post, Tag
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.
# Inline for tags
class TagInline(admin.TabularInline):  # Or you can use admin.StackedInline for a different layout
    model = Post.tags.through  # We use the `through` model for many-to-many relations
    extra = 1  # Number of empty forms to show

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Register the Post model with the TagInline
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'pub_date', 'views_count', 'get_tags')
    list_filter = ('status', 'create_date', 'pub_date', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('views_count',)
    
    # Add the TagInline so that tags can be edited within the Post form
    inlines = [TagInline]
    
    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'
