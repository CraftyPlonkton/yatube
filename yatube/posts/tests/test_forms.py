import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from ..models import Post, Group, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='test title',
            slug='test-slug',
            description='test description'
        )
        cls.post = Post.objects.create(
            pk=1,
            text='initial text',
            group=None,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormsTest.user)

    def test_valid_form_add_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test text',
            'group': PostsFormsTest.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostsFormsTest.user.username})
        )
        created_post = Post.objects.latest('pk')
        self.assertEqual(created_post.author, PostsFormsTest.user)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group, PostsFormsTest.group)
        self.assertEqual(created_post.image, 'posts/' + uploaded.name)

    def test_valid_form_edit_post(self):
        form_data = {
            'text': 'edited by authorized client text',
            'group': PostsFormsTest.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsFormsTest.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsFormsTest.post.pk})
        )
        edited_post = Post.objects.get(pk=PostsFormsTest.post.pk)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group, PostsFormsTest.group)
        self.assertEqual(edited_post.author, PostsFormsTest.user)

    def test_valid_form_add_comment(self):
        comments_count = Comment.objects.count()
        form_data = {'text': 'test comment'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostsFormsTest.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsFormsTest.post.pk})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        added_comment = Comment.objects.latest('pk')
        self.assertEqual(added_comment.post, PostsFormsTest.post)
        self.assertEqual(added_comment.author, PostsFormsTest.user)
        self.assertEqual(added_comment.text, form_data['text'])

    def test_guest_cant_add_posts(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test text',
            'group': PostsFormsTest.group.pk
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_cant_edit_posts(self):
        post_before_edit = Post.objects.get(pk=PostsFormsTest.post.pk)
        form_data = {
            'text': 'edited by guest client text',
            'group': PostsFormsTest.group.pk
        }
        self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsFormsTest.post.pk}),
            data=form_data
        )
        post_after_edit = Post.objects.get(pk=PostsFormsTest.post.pk)
        self.assertEqual(post_before_edit, post_after_edit)

    def test_guest_cant_add_comment(self):
        comments_count = Comment.objects.count()
        form_data = {'text': 'test comment'}
        self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostsFormsTest.post.pk}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comments_count)
