from django.test import TestCase, Client
from django.shortcuts import reverse
from ..models import Post, Group, User
from ..views import POSTS_ON_PAGE


class PostsPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='test title',
            slug='test-slug',
            description='test description'
        )
        for i in range(POSTS_ON_PAGE + 3):
            Post.objects.create(
                text='test text',
                group=cls.group,
                author=cls.author
            )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostsPaginatorTest.author)

    def test_paginator_page_2_show_correct_number_of_posts(self):
        urls_with_paginator = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'author'})
        )
        for url in urls_with_paginator:
            response = self.author_client.get(url + '?page=2')
            with self.subTest(url=url):
                self.assertEqual(len(response.context['page_obj']), 3)
