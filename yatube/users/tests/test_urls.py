from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_users_urls_exist_at_desired_location(self):
        """Проверяем общедоступные страницы."""
        urls = ['/auth/signup/', '/auth/login/', '/auth/logout/',
                '/auth/password_reset/', '/auth/password_reset/done/',
                '/auth/reset/<uidb64>/<token>/', '/auth/reset/done/']
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Проверьте url страницы {url}')

    def test_users_auth_urls_exist_at_desired_location(self):
        """Проверяем доступные для авторизованного пользователя страницы."""
        urls = ['/auth/password_change/', '/auth/password_change/done/']
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Проверьте url страницы {url}')

    def test_users_auth_urls_redirect_anonymous_on_login(self):
        """Проверяем, что страницы для авторизованного пользователя перенаправят
           анонимного пользователя на страницу авторизации.
        """
        url_redirect = {'/auth/password_change/':
                        '/auth/login/?next=/auth/password_change/',
                        '/auth/password_change/done/':
                        '/auth/login/?next=/auth/password_change/done/'}
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)
