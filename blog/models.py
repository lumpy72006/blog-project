from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    create_date= models.DateTimeField(auto_now_add=True) #tracks when post was created 
    pub_date= models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)
    featured_image = models.ImageField(upload_to='featured_images/', blank=True, null=True)  # Featured Image
    views_count = models.PositiveIntegerField(default=0)  # Tracks post views
    

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def increment_views(self):
        """Increment the views count for the post."""
        self.views_count += 1
        self.save()

    def save(self, *args, **kwargs):
        # Ensure the slug is unique
        if not self.slug:
            self.slug = slugify(self.title)

        # if this is a new post(no primary key yet)
        if not self.pk:
            # Check if the slug already exists, and if so, add a suffix to make it unique
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)
