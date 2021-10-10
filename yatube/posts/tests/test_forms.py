import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.shortcuts import get_object_or_404

from posts.models import Group, Post

User = get_user_model()


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(title='Котики', slug='cat',
                                         description='Про котиков')
        cls.post = Post.objects.create(author=cls.user, text='Текст о котике',
                                       group=cls.group)

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostsFormsTests.user)

    def test_posts_form_create_post(self):
        """Валидная форма создает новый пост."""
        posts_count = Post.objects.count()
        group = PostsFormsTests.group.id
        form_data = {'author': PostsFormsTests.user,
                     'text': 'Текст о котике №2',
                     'group': group}
        response = self.auth_client.post(reverse('posts:post_create'),
                                         data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
        self.assertRedirects(response, reverse('posts:profile',
                             args=[PostsFormsTests.user.username]))
        post = get_object_or_404(Post, text=form_data['text'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, form_data['author'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_posts_form_create_anonymous_not_create_post(self):
        """Анонимный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        group = PostsFormsTests.group.id
        form_data = {'author': PostsFormsTests.user,
                     'text': 'Текст о котике №3',
                     'group': group}
        response = self.guest_client.post(reverse('posts:post_create'),
                                          data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count)
        page = reverse('users:login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, page)

    def test_posts_form_edit_post(self):
        """Валидная форма редактирует пост."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст о котике №1'}
        response = self.auth_client.post(reverse('posts:post_edit',
                                         args=[PostsFormsTests.post.pk]),
                                         data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args=[PostsFormsTests.post.pk]))

    def test_posts_comment_anonymous_not_comment(self):
        """Анонимный пользователь не может комментировать пост."""
        comments_count = PostsFormsTests.post.comments.count()
        form_data = {'text': 'Тестовый комментарий'}
        response = self.guest_client.post(reverse('posts:add_comment',
                                          args=[PostsFormsTests.post.pk]),
                                          data=form_data, follow=True)
        self.assertEqual(PostsFormsTests.post.comments.count(), comments_count)
        page = (reverse('users:login') + '?next=' + reverse(
                'posts:add_comment', args=[PostsFormsTests.post.pk]))
        self.assertRedirects(response, page)

    def test_posts_comment_auth_client_create_comment(self):
        """Авторизованный пользователь создаёт комментарий к посту."""
        comments_count = PostsFormsTests.post.comments.count()
        form_data = {'text': 'Тестовый комментарий'}
        response = self.auth_client.post(reverse('posts:add_comment',
                                         args=[PostsFormsTests.post.pk]),
                                         data=form_data, follow=True)
        self.assertEqual(PostsFormsTests.post.comments.count(),
                         comments_count + 1)
        comment = PostsFormsTests.post.comments.last()
        self.assertEqual(comment.text, form_data['text'])
        page = reverse('posts:post_detail', args=[PostsFormsTests.post.pk])
        self.assertRedirects(response, page)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='jack')
        cls.group = Group.objects.create(title='Ипотека', slug='mortgage',
                                         description='Про ипотеку')
        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(name='small.gif',
                                          content=cls.small_gif,
                                          content_type='image/gif')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(ImageFormsTest.user)

    def test_posts_form_create_post_with_image(self):
        """Валидная форма создает новый пост с картинкой."""
        posts_count = Post.objects.count()
        group = ImageFormsTest.group.id
        form_data = {'author': ImageFormsTest.user,
                     'text': 'Текст об ипотеке №2',
                     'group': group, 'image': ImageFormsTest.uploaded}
        self.authorized_client.post(reverse('posts:post_create'),
                                    data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count + 1)
