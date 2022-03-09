from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from ..models import Post, Group, Comment

User = get_user_model()


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='not_author')
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='test title',
            slug='test-slug',
            description='test description'
        )
        cls.post = Post.objects.create(
            pk=1,
            text='first text',
            group=cls.group,
            author=cls.author
        )
        Post.objects.create(
            pk=2,
            text='second text',
            group=None,
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='test comment'
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(PostsViewsTest.author)

    def test_pages_use_correct_template(self):
        names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostsViewsTest.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostsViewsTest.author.username}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsViewsTest.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsViewsTest.post.pk}):
            'posts/create_post.html'
        }
        for name, template in names_templates.items():
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = self.author_client.get(reverse('posts:index'))
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)

    def test_group_posts_context(self):
        response = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostsViewsTest.group.slug})
        )
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.group.title, PostsViewsTest.group.title)

    def test_profile_context(self):
        response = self.author_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostsViewsTest.author.username})
        )
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)
            self.assertEqual(
                post.author.username,
                PostsViewsTest.author.username
            )

    def test_post_detail_context(self):
        response = self.author_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsViewsTest.post.pk})
        )
        post = response.context['post']
        self.assertIsInstance(post, Post)
        self.assertEqual(post, PostsViewsTest.post)
        comment = response.context['comments'][0]
        self.assertEqual(comment, PostsViewsTest.comment)

    def test_post_create_context(self):
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        response = self.author_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsViewsTest.post.pk})
        )
        fields_values = {
            'text': PostsViewsTest.post.text,
            'group': PostsViewsTest.post.group.pk
        }
        for field, expected in fields_values.items():
            with self.subTest(field=field):
                field_value = response.context['form'][field].value()
                self.assertEqual(field_value, expected)
