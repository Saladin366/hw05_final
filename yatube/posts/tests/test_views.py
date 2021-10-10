import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from time import sleep

from posts.models import Group, Post, Follow

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='leo')
        cls.user_2 = User.objects.create_user(username='nick')
        cls.group_1 = Group.objects.create(title='Котики',
                                           slug='cat',
                                           description='Про котиков')
        cls.group_2 = Group.objects.create(title='Здоровье',
                                           slug='health',
                                           description='Про здоровье')
        cls.post_1 = Post.objects.create(author=cls.user_1,
                                         text='Текст про котика',
                                         group=cls.group_1)
        sleep(0.1)
        cls.post_2 = Post.objects.create(author=cls.user_2,
                                         text='Текст про здоровье',
                                         group=cls.group_2)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user_1)

    def test_posts_pages_uses_correct_template(self):
        """Проверяем, что name_URL-адрес использует соответствующий шаблон."""
        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=[PostsPagesTests.group_1.slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[PostsPagesTests.user_1.username]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[PostsPagesTests.post_1.pk]):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args=[PostsPagesTests.post_1.pk]):
                'posts/create_post.html'}
        for page, template in pages_templates_names.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_count_posts_on_pages(self):
        """На страницы с сообщениями передано правильное кол-во постов."""
        posts_on_page = {reverse('posts:index'): 2,
                         reverse('posts:group_list',
                                 args=[PostsPagesTests.group_1.slug]): 1,
                         reverse('posts:group_list',
                                 args=[PostsPagesTests.group_2.slug]): 1,
                         reverse('posts:profile',
                                 args=[PostsPagesTests.user_1.username]): 1,
                         reverse('posts:profile',
                                 args=[PostsPagesTests.user_2.username]): 1
                         }
        for page, count_posts in posts_on_page.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 count_posts)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        content = [(PostsPagesTests.post_2.author.username,
                    PostsPagesTests.post_2.text,
                    PostsPagesTests.post_2.group.title),
                   (PostsPagesTests.post_1.author.username,
                    PostsPagesTests.post_1.text,
                    PostsPagesTests.post_1.group.title)]
        for i in range(len(content)):
            post = response.context['page_obj'][i]
            username = post.author.username
            text = post.text
            group = post.group.title
            fields_content = {username: content[i][0], text: content[i][1],
                              group: content[i][2]}
            for field, expected in fields_content.items():
                with self.subTest(field=field):
                    self.assertEqual(field, expected)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        groups = {PostsPagesTests.group_1.slug: PostsPagesTests.group_1.title,
                  PostsPagesTests.group_2.slug: PostsPagesTests.group_2.title}
        for page, group in groups.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse('posts:group_list', args=[page]))
                post = response.context['page_obj'][0]
                self.assertEqual(post.group.title, group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        usernames = {PostsPagesTests.user_1.username:
                     PostsPagesTests.user_1.username,
                     PostsPagesTests.user_2.username:
                     PostsPagesTests.user_2.username}
        for page, author in usernames.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse('posts:profile', args=[page]))
                post = response.context['page_obj'][0]
                self.assertEqual(post.author.username, author)

    def test_post_detail_page_have_object_post(self):
        """Страница post_detail содержит объект модели Post."""
        page_objects = {PostsPagesTests.post_1.pk: Post,
                        PostsPagesTests.post_2.pk: Post}
        for page, model in page_objects.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse('posts:post_detail', args=[page]))
                obj = response.context['post']
                self.assertIsInstance(obj, model)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        id_posts = {PostsPagesTests.post_1.pk: PostsPagesTests.post_1.pk,
                    PostsPagesTests.post_2.pk: PostsPagesTests.post_2.pk}
        for page, id in id_posts.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse('posts:post_detail', args=[page]))
                post = response.context['post']
                self.assertEqual(post.pk, id)

    def test_create_post_page_show_correct_context(self):
        """Страница создания поста создана с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {'group': forms.models.ModelChoiceField,
                       'text': forms.fields.CharField}
        for field, type_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, type_field)

    def test_edit_post_page_show_correct_context(self):
        """Страница редакторования поста создана с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[PostsPagesTests.post_1.pk]))
        form_fields = {'group': forms.models.ModelChoiceField,
                       'text': forms.fields.CharField}
        for field, type_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, type_field)
        id_post = response.context['post'].pk
        self.assertEqual(id_post, PostsPagesTests.post_1.pk)

    def test_posts_cashe_index(self):
        """Проверяем кеширование главной страницы."""
        posts_count = Post.objects.count()
        response_content = (
            self.authorized_client.get(reverse('posts:index')).content)
        Post.objects.create(author=PostsPagesTests.user_1, text='text')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            response_content,
            self.authorized_client.get(reverse('posts:index')).content)
        cache.clear()
        self.assertNotEqual(
            response_content,
            self.authorized_client.get(reverse('posts:index')).content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mick')
        cls.group = Group.objects.create(title='Финансы', slug='finance',
                                         description='Про финансы')
        cls.count_posts = 13
        for i in range(cls.count_posts):
            Post.objects.create(author=cls.user,
                                text=f'Текст про финансы №{i}',
                                group=cls.group)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_paginator(self):
        """Paginator работает согласно ожиданиям."""
        pages = (reverse('posts:index'),
                 reverse('posts:group_list',
                         args=[PaginatorViewsTest.group.slug]),
                 reverse('posts:profile',
                         args=[PaginatorViewsTest.user.username]))
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageViewsTests(TestCase):
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
        cls.post = Post.objects.create(author=cls.user,
                                       text='Текст про ипотеку',
                                       group=cls.group, image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(ImageViewsTests.user)

    def test_context_has_image(self):
        """У страниц с постами изображение передаётся в словаре context."""
        pages = (reverse('posts:index'),
                 reverse('posts:group_list',
                         args=[ImageViewsTests.group.slug]),
                 reverse('posts:profile',
                         args=[ImageViewsTests.user.username]))
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.context['page_obj'][0].image,
                                 ImageViewsTests.post.image)

    def test_post_detail_has_image(self):
        """В страницу поста изображение передаётся в словаре context."""
        response = self.client.get(reverse('posts:post_detail',
                                   args=[ImageViewsTests.post.pk]))
        self.assertEqual(response.context['post'].image,
                         ImageViewsTests.post.image)


class FollowsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='leo')
        cls.user2 = User.objects.create_user(username='nick')

    def setUp(self):
        self.auth_client1 = Client()
        self.auth_client1.force_login(FollowsTests.user1)
        self.auth_client2 = Client()
        self.auth_client2.force_login(FollowsTests.user2)

    def test_posts_auth_add_delete_follow(self):
        """Авторизованный пользователь может добавить подписку."""
        follows_count = Follow.objects.count()
        self.assertFalse(Follow.objects.filter(
            user=FollowsTests.user1,
            author=FollowsTests.user2).exists())
        self.auth_client1.get(reverse('posts:profile_follow',
                                      args=[FollowsTests.user2]))
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=FollowsTests.user1, author=FollowsTests.user2).exists())

    def test_posts_auth_add_delete_follow(self):
        """Авторизованный пользователь может удалить подписку."""
        Follow.objects.get_or_create(user=FollowsTests.user1,
                                     author=FollowsTests.user2)
        follows_count = Follow.objects.count()
        self.auth_client1.get(reverse('posts:profile_unfollow',
                                      args=[FollowsTests.user2]))
        self.assertEqual(Follow.objects.count(), follows_count - 1)
        self.assertFalse(Follow.objects.filter(
            user=FollowsTests.user1, author=FollowsTests.user2).exists())

    def test_posts_new_post_add_to_follower(self):
        """Новый пост пользователя появляется в ленте подписанных."""
        Follow.objects.create(user=FollowsTests.user2,
                              author=FollowsTests.user1)
        response = self.auth_client2.get(reverse('posts:follow_index'))
        count_posts = len(response.context['page_obj'])
        Post.objects.create(author=FollowsTests.user1, text='new_text')
        response = self.auth_client2.get(reverse('posts:follow_index'))
        new_count_posts = len(response.context['page_obj'])
        self.assertEqual(count_posts + 1, new_count_posts)

    def test_posts_new_post_not_add_to_not_follower(self):
        """Новый пост пользователя не появляется в ленте неподписанных."""
        response = self.auth_client2.get(reverse('posts:follow_index'))
        count_posts = len(response.context['page_obj'])
        Post.objects.create(author=FollowsTests.user1, text='new_text')
        response = self.auth_client2.get(reverse('posts:follow_index'))
        new_count_posts = len(response.context['page_obj'])
        self.assertEqual(count_posts, new_count_posts)
