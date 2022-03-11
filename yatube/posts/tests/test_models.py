from django.test import TestCase
from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='название',
            slug='слаг',
            description='описание'
        )
        cls.post = Post.objects.create(
            text='текст' * 10,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        post = PostModelTest.post
        models_str_text = {group: group.title, post: post.text[:15]}
        for model, expected_value in models_str_text.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), expected_value)
