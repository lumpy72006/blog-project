from django.contrib.auth.models import User
from django.http import response
from django.test import TestCase, RequestFactory
from .models import Post, Comment
from django.template import Template, Context
from .forms import CommentForm, PostForm, SignupForm
from django.urls import resolve


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
        self.assertEqual(len(form.errors), 4) #from django.urls import reverse


class SearchFunctionalityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(
            username='author1',
            password='testpass123'
        )
        cls.user2 = User.objects.create_user(
            username='author2',
            password='testpass123'
        )
        
        # Create test posts
        cls.post1 = Post.objects.create(
            title='Django Testing Guide',
            content='Comprehensive guide to testing in Django',
            author=cls.user1,
            status='published'
        )
        cls.post2 = Post.objects.create(
            title='Python Best Practices',
            content='How to write clean Python code',
            author=cls.user2,
            status='published'
        )
        cls.draft_post = Post.objects.create(
            title='Unpublished Post',
            content='This should not appear in search',
            author=cls.user1,
            status='draft'
        )

    def test_search_by_post_title(self):
        """Test searching by post title"""
        response = self.client.get(reverse('blog:search') + '?query=Django')
        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)
        self.assertNotContains(response, self.draft_post.title)

    def test_search_by_post_content(self):
        """Test searching by post content"""
        response = self.client.get(reverse('blog:search') + '?query=clean')
        self.assertContains(response, self.post2.title)
        self.assertNotContains(response, self.post1.title)

    def test_search_by_author_username(self):
        """Test searching by author username"""
        response = self.client.get(reverse('blog:search') + '?query=author1')
        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)

    def test_search_by_tags(self):
        """Test that posts can be searched with tags"""
        self.post1.tags.add('django', 'testing')
        response = self.client.get(reverse('blog:search') +'?query=django')
        self.assertContains(response, self.post1.title)

    def test_empty_search_returns_nothing(self):
        """Test empty search query returns no results"""
        response = self.client.get(reverse('blog:search') + '?query=')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)

    def test_draft_posts_not_in_search(self):
        """Test draft posts don't appear in search results"""
        response = self.client.get(reverse('blog:search') + '?query=Unpublished')
        self.assertNotContains(response, self.draft_post.title)

    def test_search_template_used(self):
        """Test that the correct template is used"""
        response = self.client.get(reverse('blog:search') + '?query=Django')
        self.assertTemplateUsed(response, 'blog/_post_list.html')

    def test_search_context_data(self):
        """Test that search results are in context"""
        response = self.client.get(reverse('blog:search') + '?query=Django')
        self.assertIn('post_list', response.context)
        self.assertEqual(len(response.context['post_list']), 1)
        self.assertEqual(response.context['post_list'][0], self.post1)


class SearchTemplateTagTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
    def render_template(self, url_name, *args, **kwargs):
        """Helper to render template with context"""
        url = reverse(url_name, args=args, kwargs=kwargs)
        request = self.factory.get(url)
        request.resolver_match = resolve(url)
        template = Template(
            '{% load blog_tags %}'
            '{% should_hide_search as hide_search %}'
            '{% if hide_search %}HIDDEN{% else %}VISIBLE{% endif %}'
        )
        return template.render(Context({'request': request}))

    def test_search_bar_visibility(self):
        """Test search bar visibility on different views"""
        # Should be visible
        self.assertEqual(self.render_template('blog:index').strip(), 'VISIBLE')
        self.assertEqual(self.render_template('blog:search').strip(), 'VISIBLE')
        
        # Should be hidden
        self.assertEqual(self.render_template('blog:signup').strip(), 'HIDDEN')
        self.assertEqual(self.render_template('blog:login').strip(), 'HIDDEN')
        self.assertEqual(self.render_template('blog:create_post').strip(), 'HIDDEN')
