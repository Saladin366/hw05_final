from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_location(self):
        """Проверяем, что страницы /about/author/ и /about/tech/ доступны."""
        urls = ['/about/author/', '/about/tech/']
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Проверьте url страницы {url}')

    def test_about_pages_uses_correct_template(self):
        """Статичные страницы about используют соответствующие шаблоны."""
        pages_templates_names = {reverse('about:author'): 'about/author.html',
                                 reverse('about:tech'): 'about/tech.html'}
        for page, template in pages_templates_names.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(response, template)
