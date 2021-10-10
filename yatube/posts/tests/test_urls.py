from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.not_author = User.objects.create_user(username='nick')
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test_slug',
                                         description='Тестовое описание')
        cls.post = Post.objects.create(author=cls.user,
                                       text='Текст тестового поста')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.client_not_author = Client()
        self.client_not_author.force_login(PostsURLTests.not_author)

    def test_posts_urls_exist_at_desired_location(self):
        """Проверяем общедоступные страницы."""
        urls = ['/', '/group/test_slug/', '/profile/leo/', '/posts/1/',
                '/unexisting_page/']
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                status = (HTTPStatus.NOT_FOUND if url == '/unexisting_page/'
                          else HTTPStatus.OK)
                self.assertEqual(response.status_code, status,
                                 f'Проверьте url страницы {url}')

    def test_posts_create_url_exists_at_desired_location(self):
        """Проверяем страницу /create/ для авторизованного пользователя."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Проверьте url страницы /create/')

    def test_posts_posts_post_id_edit_url_exists_at_desired_location(self):
        """Проверяем страницу /posts/<post_id>/edit/ для автора сообщения."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Проверьте url страницы /posts/<post_id>/edit/')

    def test_posts_create_post_edit_redirect_anonymous_on_login(self):
        """Проверяем, что страницы /create/ и /posts/<post_id>/edit/ перенаправят
           анонимного пользователя на страницу авторизации.
        """
        url_redirect = {'/create/': '/auth/login/?next=/create/',
                        '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/'}
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_posts_post_edit_url_redirect_not_author_on_post_id(self):
        """Проверяем, что страница /posts/<post_id>/edit/ перенаправит не автора
           поста на страницу сообщения.
        """
        response = self.client_not_author.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        url_templates_names = {'/': 'posts/index.html',
                               '/group/test_slug/': 'posts/group_list.html',
                               '/profile/leo/': 'posts/profile.html',
                               '/posts/1/': 'posts/post_detail.html',
                               '/create/': 'posts/create_post.html',
                               '/posts/1/edit/': 'posts/create_post.html',
                               '/unexisting_page/': 'core/404.html'}
        for url, template in url_templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
