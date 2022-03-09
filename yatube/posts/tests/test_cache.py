from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post

User = get_user_model()


class TestPostsCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')

    def setUp(self):
        self.client = Client()
        self.client.force_login(TestPostsCache.user)
        Post.objects.create(
            author=TestPostsCache.user,
            text='test text'
        )

    def test_index_page_cached(self):
        response_1 = self.client.get(reverse('posts:index'))
        content_1 = response_1.content
        Post.objects.all().delete()
        response_2 = self.client.get(reverse('posts:index'))
        content_2 = response_2.content
        self.assertEqual(content_1, content_2)
        cache.clear()
        response_3 = self.client.get(reverse('posts:index'))
        content_3 = response_3.content
        self.assertNotEqual(content_1, content_3)
