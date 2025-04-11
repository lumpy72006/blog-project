from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager


# Create your models here.
class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="published"
    )
    create_date = models.DateTimeField(auto_now_add=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()
    featured_image = models.ImageField(
        upload_to="featured_images/", blank=True, null=True
    )
    views_count = models.PositiveIntegerField(default=0)  # Tracks post views
    likes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    featured = models.BooleanField(default=False)
    reading_time = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-pub_date"]
        indexes = [
            models.Index(fields=["slug"], name="slug_idx"),
            models.Index(fields=["pub_date"], name="pub_date_idx"),
            models.Index(fields=["status"], name="status_idx"),
        ]

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.slug])

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

        # If this is a new post(no primary key yet)

        if not self.pk:
            # Check if the slug already exists, and if so, add a suffix to make it unique
            original_slug = self.slug
            counter = 1

            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Calculate reading time
        word_count = len(self.content.split())
        self.reading_time = max(1, round(word_count / 200))
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)


    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

    class Meta:
        ordering = ["-created_date"]
