from django.test import TestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Post, Category
from .forms import PostForm
from .views import IndexView, PostDetailView, create_post


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            author=self.user,
            status="published",
            category=self.category,
            excerpt="Test excerpt",
            featured=True,
        )

    def test_post_creation(self):
        """Test that a post is created correctly."""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.content, "This is a test post.")
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.status, "published")
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.excerpt, "Test excerpt")
        self.assertTrue(self.post.featured)
        self.assertEqual(self.post.views_count, 0)
        self.assertEqual(self.post.likes, 0)
        self.assertEqual(
            self.post.reading_time, 1
        )  # Default reading time for short content

    def test_increment_views(self):
        """Test the increment_views method."""
        self.post.increment_views()
        self.assertEqual(self.post.views_count, 1)

    def test_like_post(self):
        """Test liking a post."""
        self.post.liked_by.add(self.user)
        self.post.likes += 1
        self.post.save()
        self.assertEqual(self.post.likes, 1)
        self.assertIn(self.user, self.post.liked_by.all())

    def test_unlike_post(self):
        """Test unliking a post."""
        self.post.liked_by.add(self.user)
        self.post.likes += 1
        self.post.save()
        self.post.liked_by.remove(self.user)
        self.post.likes -= 1
        self.post.save()
        self.assertEqual(self.post.likes, 0)
        self.assertNotIn(self.user, self.post.liked_by.all())

    def test_reading_time_calculation(self):
        """Test the reading time calculation."""
        self.post.content = " ".join(["word"] * 400)  # 400 words
        self.post.save()
        self.assertEqual(
            self.post.reading_time, 2
        )  # 400 words / 200 words per minute = 2 minutes


class PostFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )

    def test_post_form_valid_data(self):
        """Test the PostForm with valid data."""
        form = PostForm(
            data={
                "title": "Test Post",
                "content": "This is a test post.",
                "author": self.user.id,
                "status": "published",
                "category": self.category.id,
                "excerpt": "Test excerpt",
                "featured": True,
                "tags": "test, post",
            }
        )
        self.assertTrue(form.is_valid())

    def test_post_form_invalid_data(self):
        """Test the PostForm with invalid data."""
        form = PostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)  # title, content, author, are required


class CreatePostViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        self.client.login(username="testuser", password="testpass")

    def test_create_post_view_get(self):
        """Test the GET request to the create_post view."""
        response = self.client.get(reverse("blog:create_post"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], PostForm)

    def test_create_post_view_post(self):
        """Test the POST request to the create_post view."""
        data = {
            "title": "New Post",
            "content": "This is a new post.",
            "author": self.user.id,
            "status": "published",
            "category": self.category.id,
            "excerpt": "Test excerpt",
            "featured": True,
            "tags": "test, post",
        }
        response = self.client.post(reverse("blog:create_post"), data)
        self.assertEqual(response.status_code, 302)  # Redirects to post detail
        self.assertTrue(Post.objects.filter(title="New Post").exists())


class LikePostViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            author=self.user,
            status="published",
        )
        self.client.login(username="testuser", password="testpass")

    def test_like_post(self):
        """Test liking a post."""
        response = self.client.post(reverse("blog:like_post", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"likes": 1, "user_has_liked": True})
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes, 1)
        self.assertIn(self.user, self.post.liked_by.all())

    def test_unlike_post(self):
        """Test unliking a post."""
        self.post.liked_by.add(self.user)
        self.post.likes += 1
        self.post.save()
        response = self.client.post(reverse("blog:like_post", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"likes": 0, "user_has_liked": False})
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes, 0)
        self.assertNotIn(self.user, self.post.liked_by.all())


class IndexViewTest(TestCase):
    def setUp(self):
        # Create published and draft posts
        self.published_post = Post.objects.create(
            title="Published Post",
            content="This is a published post.",
            author=User.objects.create_user(username="author", password="testpass"),
            status="published",
        )
        self.draft_post = Post.objects.create(
            title="Draft Post",
            content="This is a draft post.",
            author=User.objects.create_user(username="author2", password="testpass"),
            status="draft",
        )

    def test_index_view_returns_published_posts(self):
        """Test that only published posts are returned."""
        response = self.client.get(reverse("blog:index"))
        self.assertContains(response, self.published_post.title)
        self.assertNotContains(response, self.draft_post.title)


class PostDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            author=self.user,
            status="published",
        )

    def test_post_detail_view(self):
        """Test that the post detail view displays the correct post."""
        url = reverse("blog:post_detail", args=[self.post.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_detail_view_increments_views(self):
        """Test that the view count is incremented when viewing a post."""
        url = reverse("blog:post_detail", args=[self.post.slug])
        self.client.get(url)
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)

    def test_post_detail_view_context(self):
        """Test that the context contains likes, reading_time, and user_has_liked."""
        url = reverse("blog:post_detail", args=[self.post.slug])
        response = self.client.get(url)
        self.assertEqual(response.context["likes"], self.post.likes)
        self.assertEqual(response.context["reading_time"], self.post.reading_time)
        self.assertEqual(response.context["user_has_liked"], False)


class URLTests(TestCase):
    """Test case for URL routing."""

    def test_index_url(self):
        """Test that the index URL is correctly mapped."""
        url = reverse("blog:index")
        self.assertEqual(resolve(url).func.view_class, IndexView)

    def test_post_detail_url(self):
        """Test that the post detail URL is correctly mapped."""
        post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            author=User.objects.create_user(username="author", password="testpass"),
            status="published",
        )
        url = reverse("blog:post_detail", args=[post.slug])
        self.assertEqual(resolve(url).func.view_class, PostDetailView)

    def test_create_post_url(self):
        """Test that the create post URL is correctly mapped."""
        url = reverse("blog:create_post")
        self.assertEqual(resolve(url).func, create_post)


class PostUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            author=self.user,
            status="published",
        )
        self.client.login(username="testuser", password="testpass")

    def test_edit_post_view_get(self):
        """Test the GET request to the edit_post view."""
        response = self.client.get(reverse("blog:edit_post", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Post")

    def test_edit_post_view_post(self):
        """Test the POST request to the edit_post view."""
        data = {
            "title": "Updated Post",
            "content": "This is an updated post.",
            "status": "published",
        }
        response = self.client.post(
            reverse("blog:edit_post", args=[self.post.slug]), data
        )
        self.assertEqual(response.status_code, 302)  # Redirects to post detail
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Post")
        self.assertEqual(self.post.content, "This is an updated post.")

    def test_edit_post_view_unauthorized(self):
        """Test that non-authors cannot edit the post."""
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.client.login(username="otheruser", password="testpass")
        response = self.client.get(reverse("blog:edit_post", args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)  # Forbidden


class PostDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            author=self.user,
            status="published",
        )
        self.client.login(username="testuser", password="testpass")

    def test_delete_post_view_get(self):
        """Test the GET request to the delete_post view."""
        response = self.client.get(reverse("blog:delete_post", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Post")

    def test_delete_post_view_post(self):
        """Test the POST request to the delete_post view."""
        response = self.client.post(reverse("blog:delete_post", args=[self.post.slug]))
        self.assertEqual(response.status_code, 302)  # Redirects to home page
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_view_unauthorized(self):
        """Test that non-authors cannot delete the post."""
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.client.login(username="otheruser", password="testpass")
        response = self.client.get(reverse("blog:delete_post", args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)  # Forbidden
