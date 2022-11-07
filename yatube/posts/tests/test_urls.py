from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="not_author")
        cls.author = User.objects.create(username="author")
        cls.group = Group.objects.create(
            title="test title",
            slug="test-slug",
            description="test description"
        )
        Post.objects.create(
            text="test text",
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(PostsUrlsTest.user)
        self.author_client = Client()
        self.author_client.force_login(PostsUrlsTest.author)

    def test_posts_urls_response_to_guest(self):
        urls_responses = {
            "/": HTTPStatus.OK,
            f"/group/{PostsUrlsTest.group.slug}/": HTTPStatus.OK,
            f"/profile/{PostsUrlsTest.author.username}/": HTTPStatus.OK,
            f"/posts/{PostsUrlsTest.group.pk}/": HTTPStatus.OK,
            f"/posts/{PostsUrlsTest.group.pk}/edit/": HTTPStatus.FOUND,
            "/create/": HTTPStatus.FOUND,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, code in urls_responses.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_redirect_guest_to_login_page(self):
        urls_redirects = {
            f"/posts/{PostsUrlsTest.group.pk}/edit/":
                f"/auth/login/?next=/posts/{PostsUrlsTest.group.pk}/edit/",
            "/create/":
                "/auth/login/?next=/create/",
        }
        for url, redirect in urls_redirects.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_posts_urls_response_to_authorised_user(self):
        urls_responses = {
            "/": HTTPStatus.OK,
            f"/group/{PostsUrlsTest.group.slug}/": HTTPStatus.OK,
            f"/profile/{PostsUrlsTest.author.username}/": HTTPStatus.OK,
            f"/posts/{PostsUrlsTest.group.pk}/": HTTPStatus.OK,
            f"/posts/{PostsUrlsTest.group.pk}/edit/": HTTPStatus.FOUND,
            "/create/": HTTPStatus.OK,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, code in urls_responses.items():
            with self.subTest(url=url):
                response = self.authorised_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_post_edit_redirect_not_author_to_post_detail(self):
        response = self.authorised_client.get(
            f"/posts/{PostsUrlsTest.group.pk}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{PostsUrlsTest.group.pk}/")

    def test_post_edit_url_response_to_author(self):
        response = self.author_client.get(
            f"/posts/{PostsUrlsTest.group.pk}/edit/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        urls_templates = {
            "/": "posts/index.html",
            f"/group/{PostsUrlsTest.group.slug}/": "posts/group_list.html",
            f"/profile/{PostsUrlsTest.author.username}/": "posts/profile.html",
            f"/posts/{PostsUrlsTest.group.pk}/": "posts/post_detail.html",
            f"/posts/{PostsUrlsTest.group.pk}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
