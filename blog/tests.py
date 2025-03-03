from django.contrib.auth.models import User
from django.test import TestCase
from .models import Post, Comment


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the entire test class.
        This method is called once, before any test methods are run.
        """
        # Create a user and a post for testing
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a test post.",
            author=cls.user,
            status="published",
        )

    def test_post_creation(self):
        """Test that a post is created correctly."""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.slug, "test-post")
        self.assertEqual(self.post.content, "This is a test post.")
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.status, "published")

    def test_post_str_method(self):
        """Test the __str__ method of the Post model."""
        self.assertEqual(str(self.post), "Test Post")

    def test_slug_uniqueness(self):
        """ Test slug uniqueness with the same title """
        post = Post(
            title="Test Post",
            content="This is a test post.",
            author=self.user,
        )
        post.save()
        self.assertNotEqual(post.slug, self.post.slug)
        self.assertTrue(post.slug.endswith("-1"))

    def test_reading_time_calculation(self):
        """Test the calculation of the reading time for a post."""
        post = Post(
            title="Another Test Post",
            content="This is another test post.",
            author=self.user,
        )
        post.save()
        self.assertGreater(post.reading_time, 0)

    def test_post_get_absolute_url_method(self):
        """Test the get_absolute_url method of the Post model."""
        self.assertEqual(self.post.get_absolute_url(), "/test-post/")

    def test_post_save_method(self):
        """Test the save method of the Post model."""
        post = Post(
            title="Another Test Post",
            content="This is another test post.",
            author=self.user,
        )
        post.save()
        self.assertTrue(post.slug.startswith("another-test-post"))
        self.assertGreater(post.reading_time, 0)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user, a post, and a comment for testing
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a test post.",
            author=cls.user,
            status="published",
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            content="This is a test comment.",
        )

    def test_comment_creation(self):
        """Test that a comment is created correctly."""
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, "This is a test comment.")
        self.assertTrue(self.comment.approved)

    def test_comment_str_method(self):
        """Test the __str__ method of the Comment model."""
        self.assertEqual(str(self.comment), "Comment by testuser on Test Post")


# Test Views
from django.urls import reverse

class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user and a published post for testing
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a test post.",
            author=cls.user,
            status="published",
        )

    def test_index_view(self):
        """Test that the index view returns published posts."""
        response = self.client.get(reverse("blog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")
        self.assertQuerySetEqual(
            response.context["post_list"],
            Post.objects.filter(status="published").order_by("-pub_date") # type: ignore
        )


class PostDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user, a post, and a comment for testing
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a test post.",
            author=cls.user,
            status="published",
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            content="This is a test comment.",
        )

    def test_post_detail_view(self):
        """Test that the post detail view returns the correct post."""
        response = self.client.get(reverse("blog:post_detail", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")
        self.assertContains(response, "This is a test comment.")

    def test_post_detail_view_increments_views(self):
        """Test that the post detail view increments the views count."""
        initial_views = self.post.views_count
        self.client.get(reverse("blog:post_detail", args=[self.post.slug]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, initial_views + 1)


class LikePostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user and a post for testing
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a test post.",
            author=cls.user,
            status="published",
        )

    def test_like_post_view(self):
        """Test that the like_post view toggles likes correctly."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("blog:like_post", args=[self.post.slug]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["likes"], 1)
        self.assertTrue(response.json()["user_has_liked"])

        # Unlike the post
        response = self.client.post(
            reverse("blog:like_post", args=[self.post.slug]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["likes"], 0)
        self.assertFalse(response.json()["user_has_liked"])

# test forms
from .forms import CommentForm, PostForm, SignupForm

class PostFormTest(TestCase):
    def test_post_form_valid_data(self):
        """ Test the PostForm with valid data """
        form_data = {
            'title': 'Test Post',
            'content': 'This is a test post content.',
            'status': 'published'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_no_data(self):
        """ Test the PostForm with no data """
        form = PostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)  # title, content, and status are required

class CommentFormTest(TestCase):
    def test_comment_form_valid_data(self):
        """ Test the CommentForm with valid data """
        form_data = {
            'content': 'This is a test comment content.'
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_no_data(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1) # content is required

class SignupFormTest(TestCase):
    def test_signup_form_valid_data(self):
        """ Test the SignupForm with valid data """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_signup_form_no_data(self):
        """ Test the SignupForm with no data """
        form = SignupForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4) # username, email, password1, and password2 are required
