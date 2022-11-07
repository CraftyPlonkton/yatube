from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post, User


class TestFollowing(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create(username="user_1")
        cls.user_2 = User.objects.create(username="user_2")
        cls.author = User.objects.create(username="author")
        cls.follow = Follow.objects.create(user=cls.user_2, author=cls.author)
        cls.post = Post.objects.create(author=cls.author, text="test text")

    def setUp(self):
        self.user_1_client = Client()
        self.user_1_client.force_login(TestFollowing.user_1)
        self.user_2_client = Client()
        self.user_2_client.force_login(TestFollowing.user_2)

    def test_uthorised_user_can_follow_unfollow_author(self):
        count_follows = Follow.objects.count()
        self.user_1_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": TestFollowing.author.username},
            )
        )
        self.assertEqual(Follow.objects.count(), count_follows + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=TestFollowing.user_1, author=TestFollowing.author
            ).exists()
        )
        self.user_1_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": TestFollowing.author.username},
            )
        )
        self.assertEqual(Follow.objects.count(), count_follows)
        self.assertFalse(
            Follow.objects.filter(
                user=TestFollowing.user_1, author=TestFollowing.author
            ).exists()
        )

    def test_follow_index_context(self):
        response_1 = self.user_1_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response_1.context["page_obj"]), 0)
        response_2 = self.user_2_client.get(reverse("posts:follow_index"))
        self.assertEqual(response_2.context["page_obj"][0], TestFollowing.post)
